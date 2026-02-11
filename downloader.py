"""
Módulo Principal de Download - VERSÃO FINAL INTEGRADA v3.2
Inclui suporte completo a materiais complementares
Parte 4/5 da refatoração
"""
import logging
import sys
import asyncio
from pathlib import Path
from typing import Optional, Callable
from playwright.async_api import async_playwright, Error as PlaywrightError
from config_manager import ConfigManager, ProgressManager, CourseUrlManager
from auth import AuthManager
from video_processor import VideoProcessor
from pdf_processor import PDFProcessor
from utils import setup_logger, PrintRedirector, DownloadMetrics

logger = logging.getLogger(__name__)


class DownloadManager:
    """Gerenciador principal que orquestra todo o processo de download"""
    
    BROWSER_TIMEOUT = 30000  # ms
    
    def __init__(self, config_manager: ConfigManager, log_queue=None):
        """
        Inicializa o gerenciador de downloads.
        
        Args:
            config_manager: Gerenciador de configurações
            log_queue: Fila para enviar logs para interface (opcional)
        """
        self.config = config_manager
        self.progress = ProgressManager()
        self.url_manager = CourseUrlManager()
        self.log_queue = log_queue
        
        self._cancel_event = asyncio.Event()
        self.metrics = DownloadMetrics()
        
        # Configura logger
        global logger
        logger = setup_logger(__name__, log_queue)
        
        # Redireciona print para logger
        sys.stdout = PrintRedirector(logger)
        
        logger.info("✓ DownloadManager inicializado")
    
    def request_cancel(self) -> None:
        """Solicita cancelamento dos downloads em andamento (thread-safe)"""
        self._cancel_event.set()
        logger.warning("⚠ Cancelamento solicitado pelo usuário")
    
    @property
    def cancel_requested(self) -> bool:
        """Verifica se cancelamento foi solicitado"""
        return self._cancel_event.is_set()
    
    async def start_downloads(
        self,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> bool:
        """
        Inicia processo de download de todos os cursos na fila.
        
        Args:
            progress_callback: Função callback para atualizar progresso (opcional)
                             Recebe um float entre 0.0 e 1.0
        
        Returns:
            True se completou com sucesso, False caso contrário
        """
        logger.info("=" * 70)
        logger.info("🚀 INICIANDO ESTRATÉGIA DOWNLOADER PRO v3.2")
        logger.info("=" * 70)
        
        # Health check
        if not await self._health_check():
            logger.error("❌ Health check falhou. Processo abortado.")
            return False
        
        # Obtém lista de URLs
        course_urls = self.url_manager.get_all()
        if not course_urls:
            logger.warning("⚠ Nenhum curso na lista para baixar")
            logger.info("   Adicione cursos na aba 'Cursos' e tente novamente")
            return False
        
        total_courses = len(course_urls)
        logger.info(f"📚 Total de cursos na fila: {total_courses}")
        logger.info("")
        
        # Inicia navegador e sessão HTTP
        playwright = None
        context = None
        session = None  # ✅ Sessão compartilhada
        
        try:
            # ✅ Inicializa sessão compartilhada uma única vez
            import aiohttp
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5, force_close=True)
            timeout = aiohttp.ClientTimeout(total=300, connect=30, sock_read=60)
            session = aiohttp.ClientSession(connector=connector, timeout=timeout)
            logger.info("🌐 Sessão HTTP compartilhada inicializada")

            playwright = await async_playwright().start()
            context = await self._launch_browser(playwright)
            page = await context.new_page()
            
            # Faz login
            await self._perform_authentication(page)
            
            # Processa cada curso
            success_count = 0
            failed_count = 0
            
            for i, course_item in enumerate(course_urls, 1):
                # Extrai URL e Título (suporte a dict e str)
                if isinstance(course_item, dict):
                    course_url = course_item.get("url")
                    course_title = course_item.get("title", f"Curso {i}")
                else:
                    course_url = course_item
                    course_title = f"Curso {i}"
                
                if self.cancel_requested:
                    logger.warning("❌ Downloads cancelados pelo usuário")
                    break
                
                logger.info("")
                logger.info("=" * 70)
                logger.info(f"📖 Processando curso {i}/{total_courses}: {course_title}")
                logger.info("=" * 70)
                logger.info(f"🔗 URL: {course_url}")
                logger.info("")
                
                # Processa o curso
                try:
                    # ✅ Passa a sessão para o processamento
                    success = await self._process_course(page, course_url, session)
                    
                    if success:
                        success_count += 1
                        logger.info(f"✅ Curso {i}/{total_courses} processado com sucesso!")
                    else:
                        failed_count += 1
                        logger.error(f"❌ Curso {i}/{total_courses} falhou")
                
                except asyncio.CancelledError:
                    logger.warning("⚠ Processamento cancelado")
                    break
                
                except Exception as e:
                    logger.error(f"❌ Erro ao processar curso {i}: {e}", exc_info=True)
                    failed_count += 1
                
                # Atualiza callback de progresso
                if progress_callback:
                    try:
                        progress_callback(i / total_courses)
                    except Exception as e:
                        logger.warning(f"⚠ Erro no callback de progresso: {e}")
            
            # Relatório final
            logger.info("")
            logger.info("=" * 70)
            logger.info("📊 RELATÓRIO FINAL")
            logger.info("=" * 70)
            logger.info(f"✅ Cursos processados com sucesso: {success_count}")
            logger.info(f"❌ Cursos com falha: {failed_count}")
            logger.info(f"📚 Total de cursos: {total_courses}")
            logger.info("=" * 70)
            
            # Estatísticas de download
            self.metrics.log_stats(logger)
            
            logger.info("=" * 70)
            logger.info("✅ PROCESSO FINALIZADO")
            logger.info("=" * 70)
            
            return failed_count == 0
        
        except asyncio.CancelledError:
            logger.warning("⚠ Processo cancelado pelo usuário")
            return False
        
        except PlaywrightError as e:
            logger.error(f"❌ Erro do Playwright: {e}", exc_info=True)
            return False
        
        except Exception as e:
            logger.error(f"❌ Erro crítico no processo: {e}", exc_info=True)
            return False
        
        finally:
            # Cleanup
            if session:
                logger.info("🔒 Fechando sessão HTTP...")
                await session.close()

            if context:
                logger.info("🔒 Fechando navegador...")
                try:
                    await context.close()
                except Exception as e:
                    logger.warning(f"⚠ Erro ao fechar contexto: {e}")
            
            if playwright:
                try:
                    await playwright.stop()
                except Exception as e:
                    logger.warning(f"⚠ Erro ao parar playwright: {e}")
            
            logger.info("✓ Recursos liberados")
    
    async def _health_check(self) -> bool:
        """Verifica integridade do ambiente antes de iniciar"""
        try:
            # Valida configurações
            is_valid, errors = self.config.validate()
            if not is_valid:
                for msg in errors:
                    logger.error(f"❌ Configuração inválida: {msg}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Falha no health check: {e}")
            return False

    async def _launch_browser(self, playwright):
        """Inicializa navegador"""
        headless = self.config.config.get("headless", False)
        logger.info(f"🌐 Iniciando navegador (headless={headless})...")
        
        browser = await playwright.chromium.launch(
            headless=headless,
            args=['--start-maximized', '--disable-infobars']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        return context

    async def _perform_authentication(self, page):
        """Realiza login na plataforma"""
        email = self.config.config.get("email")
        password = self.config.get_password()
        
        if not email or not password:
            raise ValueError("Credenciais não configuradas")
            
        auth = AuthManager(email, password)
        await auth.ensure_logged_in(page)

    async def _process_course(self, page: "Page", course_url: str, session) -> bool:
        """
        Processa um curso específico usando o processador apropriado.
        
        Args:
            page: Página do Playwright
            course_url: URL do curso
            session: Sessão aiohttp compartilhada
        
        Returns:
            True se processado com sucesso
        """
        download_type = self.config.config.get("downloadType", "pdf")
        
        try:
            # Cria processador apropriado
            if download_type == "pdf":
                processor = self._create_pdf_processor(session)
            else:
                processor = self._create_video_processor(session)
            
            # Propaga cancelamento para o processador
            if self.cancel_requested:
                processor.request_cancel()
            
            # Processa o curso
            success = await processor.process_course(page, course_url)
            
            # ✅ NOVA LÓGICA: Se for tipo PDF e tiver opção de baixar extras de vídeo habilitada
            if success and download_type == "pdf":
                baixar_extras = self.config.get("pdfConfig", "baixarExtrasComPdf", default=False)
                
                if baixar_extras:
                    logger.info("")
                    logger.info("🎬 Iniciando download de materiais complementares dos vídeos...")
                    logger.info("(Mapas Mentais, Resumos e Slides)")
                    logger.info("-" * 50)
                    
                    # Cria processador de vídeo em modo "skip_video"
                    video_processor = self._create_video_processor_for_extras(session)
                    
                    # Propaga cancelamento
                    if self.cancel_requested:
                        video_processor.request_cancel()
                    
                    # Executa
                    await video_processor.process_course(page, course_url)
            
            return success
        
        except asyncio.CancelledError:
            logger.warning("⚠ Processamento cancelado")
            return False
        
        except Exception as e:
            logger.error(f"❌ Erro ao processar curso: {e}", exc_info=True)
            return False
    
    def _create_pdf_processor(self, session) -> PDFProcessor:
        """
        Cria processador de PDF com configurações do usuário.
        
        Returns:
            Instância configurada de PDFProcessor
        """
        base_dir = Path(self.config.get("pdfConfig", "pastaDownloads"))
        pdf_type = self.config.get("pdfConfig", "pdfType", default=2)
        
        logger.info(f"📄 Criando processador de PDF (tipo: {pdf_type})")
        
        return PDFProcessor(
            base_dir=base_dir,
            progress_manager=self.progress,
            pdf_type=pdf_type,
            log_queue=self.log_queue,  # ✅ Passa fila de logs
            session=session            # ✅ Passa sessão
        )
    
    def _create_video_processor(self, session) -> VideoProcessor:
        """
        Cria processador de vídeo com configurações do usuário.
        
        Returns:
            Instância configurada de VideoProcessor
        """
        base_dir = Path(self.config.get("videoConfig", "pastaDownloads"))
        resolution = self.config.get("videoConfig", "resolucaoEscolhida", default="720p")
        
        # ✅ NOVA CONFIGURAÇÃO: Suporte a baixar extras
        download_extras = self.config.get("videoConfig", "baixarExtras", default=True)
        
        logger.info(f"🎥 Criando processador de vídeo")
        logger.info(f"   Resolução: {resolution}")
        logger.info(f"   Baixar extras: {'Sim' if download_extras else 'Não'}")
        
        return VideoProcessor(
            base_dir=base_dir,
            progress_manager=self.progress,
            preferred_resolution=resolution,
            download_extras=download_extras,  # ✅ Passa configuração para o processador
            skip_video=False,
            log_queue=self.log_queue,  # ✅ Passa fila de logs
            session=session            # ✅ Passa sessão
        )

    def _create_video_processor_for_extras(self, session) -> VideoProcessor:
        """
        Cria processador de vídeo configurado APENAS para baixar extras.
        Usa a pasta de PDFs como destino para manter tudo junto.
        """
        # Usa a pasta de PDFs como base, já que é um complemento ao download de PDFs
        base_dir = Path(self.config.get("pdfConfig", "pastaDownloads"))
        
        logger.info(f"🎥 Criando processador auxiliar para Materiais Extras")
        logger.info(f"   Destino: {base_dir}")
        
        return VideoProcessor(
            base_dir=base_dir,
            progress_manager=self.progress,
            preferred_resolution='360p', # Irrelevante pois não vai baixar vídeo
            download_extras=True,
            skip_video=True, # ✅ MODO IMPORTANTE: Pula download de vídeo
            log_queue=self.log_queue,  # ✅ Passa fila de logs
            session=session            # ✅ Passa sessão
        )


# Função auxiliar para uso standalone (linha de comando)
async def main() -> int:
    """
    Função principal para execução via linha de comando.
    
    Returns:
        Código de saída (0 = sucesso, 1 = falha)
    """
    import asyncio
    
    config = ConfigManager()
    manager = DownloadManager(config)
    
    print("\n" + "="*70)
    print("ESTRATÉGIA DOWNLOADER PRO v3.2 - Modo Linha de Comando")
    print("="*70 + "\n")
    
    try:
        success = await manager.start_downloads()
        
        if success:
            print("\n✅ Todos os downloads foram concluídos com sucesso!")
            return 0
        else:
            print("\n⚠ Alguns downloads falharam. Verifique os logs.")
            return 1
    
    except KeyboardInterrupt:
        print("\n⚠ Processo interrompido pelo usuário")
        return 130  # Código padrão para Ctrl+C
    
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        return 1


if __name__ == "__main__":
    """Permite executar diretamente: python downloader.py"""
    import asyncio
    
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠ Interrompido")
        sys.exit(130)
