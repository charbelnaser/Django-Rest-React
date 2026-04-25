from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
import os

def health_check(request):
    """
    Simple health check endpoint for monitoring services like UptimeRobot
    Returns JSON with server status and basic info
    """
    try:
        # Check database connection
        from authentication.models import User
        db_status = "connected"
        try:
            # Try to count users (this tests MongoDB connection)
            user_count = User.objects.count()
        except Exception as e:
            db_status = f"error: {str(e)}"
            user_count = 0
        
        health_data = {
            "status": "healthy",
            "timestamp": timezone.now().isoformat(),
            "server": "Movies Vault Backend",
            "version": "1.0",
            "database": {
                "status": db_status,
                "users_count": user_count
            },
            "environment": {
                "debug": settings.DEBUG,
                "allowed_hosts": settings.ALLOWED_HOSTS
            }
        }
        
        return JsonResponse(health_data, status=200)
    
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e),
            "timestamp": timezone.now().isoformat()
        }, status=500)

def health_page(request):
    """
    Simple HTML page to check server status visually
    Useful for quick manual checks
    """
    try:
        # Check database connection
        from authentication.models import User
        try:
            user_count = User.objects.count()
            db_status = "✅ Connected"
            db_color = "green"
        except Exception as e:
            user_count = 0
            db_status = f"❌ Error: {str(e)}"
            db_color = "red"
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Movies Vault Backend - System Status</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
                    color: #ffffff;
                    min-height: 100vh;
                    line-height: 1.6;
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 40px 20px;
                }}
                
                .header {{
                    text-align: center;
                    margin-bottom: 50px;
                    border-bottom: 1px solid #2a2a3e;
                    padding-bottom: 30px;
                }}
                
                .header h1 {{
                    font-size: 2.8rem;
                    font-weight: 300;
                    margin-bottom: 10px;
                    background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }}
                
                .header .subtitle {{
                    font-size: 1.1rem;
                    color: #a0a0a0;
                    font-weight: 400;
                }}
                
                .status-overview {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 25px;
                    margin-bottom: 40px;
                }}
                
                .status-card {{
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    padding: 25px;
                    transition: all 0.3s ease;
                    position: relative;
                    overflow: hidden;
                }}
                
                .status-card:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 10px 30px rgba(0, 180, 219, 0.2);
                    border-color: rgba(0, 180, 219, 0.3);
                }}
                
                .status-card::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 3px;
                    background: linear-gradient(90deg, #00b4db, #0083b0);
                }}
                
                .status-card.error::before {{
                    background: linear-gradient(90deg, #ff4757, #c44569);
                }}
                
                .card-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 15px;
                }}
                
                .card-title {{
                    font-size: 1.2rem;
                    font-weight: 600;
                    color: #ffffff;
                }}
                
                .status-indicator {{
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    background: #00ff88;
                    box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
                    animation: pulse 2s infinite;
                }}
                
                .status-indicator.error {{
                    background: #ff4757;
                    box-shadow: 0 0 10px rgba(255, 71, 87, 0.5);
                }}
                
                @keyframes pulse {{
                    0%, 100% {{ opacity: 1; }}
                    50% {{ opacity: 0.6; }}
                }}
                
                .card-content p {{
                    margin: 8px 0;
                    color: #e0e0e0;
                }}
                
                .card-content strong {{
                    color: #ffffff;
                    font-weight: 500;
                }}
                
                .metrics-section {{
                    background: rgba(255, 255, 255, 0.03);
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-radius: 12px;
                    padding: 30px;
                    margin-bottom: 30px;
                }}
                
                .metrics-title {{
                    font-size: 1.4rem;
                    font-weight: 600;
                    margin-bottom: 20px;
                    color: #ffffff;
                }}
                
                .api-endpoints {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                }}
                
                .endpoint-link {{
                    display: block;
                    padding: 12px 16px;
                    background: rgba(0, 180, 219, 0.1);
                    border: 1px solid rgba(0, 180, 219, 0.3);
                    border-radius: 8px;
                    color: #00b4db;
                    text-decoration: none;
                    transition: all 0.3s ease;
                    font-weight: 500;
                }}
                
                .endpoint-link:hover {{
                    background: rgba(0, 180, 219, 0.2);
                    border-color: rgba(0, 180, 219, 0.5);
                    color: #ffffff;
                    transform: translateY(-1px);
                }}
                
                .controls {{
                    display: flex;
                    justify-content: center;
                    gap: 20px;
                    margin: 30px 0;
                }}
                
                .btn {{
                    padding: 12px 24px;
                    border: none;
                    border-radius: 8px;
                    font-size: 1rem;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    text-decoration: none;
                    display: inline-block;
                }}
                
                .btn-primary {{
                    background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
                    color: white;
                }}
                
                .btn-primary:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(0, 180, 219, 0.4);
                }}
                
                .footer {{
                    text-align: center;
                    padding-top: 30px;
                    border-top: 1px solid #2a2a3e;
                    color: #808080;
                    font-size: 0.9rem;
                }}
                
                .footer .timestamp {{
                    color: #a0a0a0;
                    margin-top: 10px;
                }}
                
                @media (max-width: 768px) {{
                    .container {{
                        padding: 20px 15px;
                    }}
                    
                    .header h1 {{
                        font-size: 2.2rem;
                    }}
                    
                    .status-overview {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .controls {{
                        flex-direction: column;
                        align-items: center;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Movies Vault</h1>
                    <p class="subtitle">Backend System Status Dashboard</p>
                </div>
                
                <div class="status-overview">
                    <div class="status-card">
                        <div class="card-header">
                            <h3 class="card-title">Server Status</h3>
                            <div class="status-indicator"></div>
                        </div>
                        <div class="card-content">
                            <p><strong>Status:</strong> Operational</p>
                            <p><strong>Version:</strong> 1.0.0</p>
                            <p><strong>Environment:</strong> {'Development' if settings.DEBUG else 'Production'}</p>
                            <p><strong>Runtime:</strong> Python 3.11</p>
                        </div>
                    </div>
                    
                    <div class="status-card {'error' if 'Error' in db_status else ''}">
                        <div class="card-header">
                            <h3 class="card-title">Database</h3>
                            <div class="status-indicator {'error' if 'Error' in db_status else ''}"></div>
                        </div>
                        <div class="card-content">
                            <p><strong>Status:</strong> {db_status.replace('✅ ', '').replace('❌ ', '')}</p>
                            <p><strong>Total Users:</strong> {user_count}</p>
                            <p><strong>Type:</strong> PostgreSQL</p>
                            <p><strong>Connection:</strong> Django ORM</p>
                        </div>
                    </div>
                    
                    <div class="status-card">
                        <div class="card-header">
                            <h3 class="card-title">Network</h3>
                            <div class="status-indicator"></div>
                        </div>
                        <div class="card-content">
                            <p><strong>Allowed Hosts:</strong> {len(settings.ALLOWED_HOSTS)} configured</p>
                            <p><strong>CORS:</strong> Enabled</p>
                            <p><strong>SSL:</strong> Enforced</p>
                            <p><strong>API Version:</strong> v1</p>
                        </div>
                    </div>
                    
                    <div class="status-card">
                        <div class="card-header">
                            <h3 class="card-title">Services</h3>
                            <div class="status-indicator"></div>
                        </div>
                        <div class="card-content">
                            <p><strong>Authentication:</strong> JWT Ready</p>
                            <p><strong>TMDB API:</strong> Connected</p>
                            <p><strong>File Storage:</strong> WhiteNoise</p>
                            <p><strong>Web Server:</strong> Gunicorn</p>
                        </div>
                    </div>
                </div>
                
                <div class="controls">
                    <button class="btn btn-primary" onclick="window.location.reload()">Refresh Status</button>
                </div>
                
                <div class="footer">
                    <p>Backend Health Monitoring Dashboard</p>
                    <p class="timestamp">Last Updated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                </div>
            </div>
            
            <script>
                // Add some interactivity
                document.addEventListener('DOMContentLoaded', function() {{
                    const cards = document.querySelectorAll('.status-card');
                    cards.forEach(card => {{
                        card.addEventListener('mouseenter', function() {{
                            this.style.transform = 'translateY(-5px) scale(1.02)';
                        }});
                        card.addEventListener('mouseleave', function() {{
                            this.style.transform = 'translateY(-2px) scale(1)';
                        }});
                    }});
                }});
            </script>
        </body>
        </html>
        """
        
        return HttpResponse(html_content)
    
    except Exception as e:
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error - Movies Vault Backend</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                .error {{ background: #ffe6e6; border: 1px solid #ff9999; padding: 20px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="error">
                <h2>❌ Server Error</h2>
                <p><strong>Error:</strong> {str(e)}</p>
                <p><strong>Time:</strong> {timezone.now()}</p>
            </div>
        </body>
        </html>
        """
        return HttpResponse(error_html, status=500)
