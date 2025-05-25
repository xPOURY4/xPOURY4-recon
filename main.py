#!/usr/bin/env python3
"""
xPOURY4 Recon - Elite Cyber Intelligence & Digital Forensics Platform
Author: xPOURY4
Version: 1.0.0

Main entry point for the application
"""

import sys
import asyncio
import argparse
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from xPOURY4_recon.core.config_manager import config
from xPOURY4_recon.core.logger import logger
from xPOURY4_recon.core.recon_engine import ReconEngine
from xPOURY4_recon.web.app import create_app


def print_banner():
    """Print application banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║              RECON - Elite Cyber Intelligence Platform        ║
    ║                         Version 1.0.0                         ║
    ║                        Author: xPOURY4                        ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


async def run_cli_mode():
    """Run in CLI mode"""
    print_banner()
    
    recon_engine = ReconEngine()
    
    while True:
        print("\n🔍 xPOURY4 Recon - Main Menu")
        print("=" * 50)
        print("1. GitHub Reconnaissance")
        print("2. Domain Reconnaissance") 
        print("3. Phone Number OSINT")
        print("4. LinkedIn Reconnaissance")
        print("5. Shodan Intelligence")
        print("6. Comprehensive Scan")
        print("7. View Results")
        print("8. Configuration")
        print("9. Module Status")
        print("0. Exit")
        print("=" * 50)
        
        choice = input("\n🎯 Select an option: ").strip()
        
        try:
            if choice == "1":
                await handle_github_recon(recon_engine)
            elif choice == "2":
                await handle_domain_recon(recon_engine)
            elif choice == "3":
                await handle_phone_recon(recon_engine)
            elif choice == "4":
                await handle_linkedin_recon(recon_engine)
            elif choice == "5":
                await handle_shodan_recon(recon_engine)
            elif choice == "6":
                await handle_comprehensive_recon(recon_engine)
            elif choice == "7":
                display_results(recon_engine)
            elif choice == "8":
                display_configuration()
            elif choice == "9":
                display_module_status(recon_engine)
            elif choice == "0":
                print("\n👋 Thank you for using xPOURY4 Recon!")
                break
            else:
                print("❌ Invalid choice! Please try again.")
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Operation cancelled by user.")
        except Exception as e:
            logger.error(f"CLI error: {e}")
            print(f"❌ Error: {e}")


async def handle_github_recon(recon_engine):
    """Handle GitHub reconnaissance"""
    print("\n🐙 GitHub Reconnaissance")
    print("-" * 30)
    
    username = input("Enter GitHub username: ").strip()
    if not username:
        print("❌ Username is required!")
        return
    
    print(f"\n🔍 Investigating GitHub user: {username}")
    print("⏳ Please wait...")
    
    result = await recon_engine.run_github_recon(username)
    
    if result.get('success'):
        data = result.get('data', {})
        profile = data.get('profile', {})
        stats = data.get('statistics', {})
        
        print(f"\n✅ GitHub investigation completed!")
        print(f"👤 Name: {profile.get('name', 'N/A')}")
        print(f"📍 Location: {profile.get('location', 'N/A')}")
        print(f"🏢 Company: {profile.get('company', 'N/A')}")
        print(f"📂 Public Repos: {profile.get('public_repos', 0)}")
        print(f"⭐ Total Stars: {stats.get('total_stars', 0)}")
        print(f"👥 Followers: {profile.get('followers', 0)}")
    else:
        print(f"❌ Investigation failed: {result.get('error')}")


async def handle_domain_recon(recon_engine):
    """Handle domain reconnaissance"""
    print("\n🌐 Domain Reconnaissance")
    print("-" * 30)
    
    domain = input("Enter domain (e.g., example.com): ").strip()
    if not domain:
        print("❌ Domain is required!")
        return
    
    print(f"\n🔍 Investigating domain: {domain}")
    print("⏳ Please wait...")
    
    result = await recon_engine.run_domain_recon(domain)
    
    if result.get('success'):
        data = result.get('data', {})
        subdomains = data.get('subdomains', {})
        whois_data = data.get('whois', {})
        stats = data.get('statistics', {})
        
        print(f"\n✅ Domain investigation completed!")
        print(f"🏢 Registrar: {whois_data.get('registrar', 'N/A')}")
        print(f"📅 Created: {whois_data.get('creation_date', 'N/A')}")
        print(f"🔍 Subdomains found: {stats.get('total_subdomains', 0)}")
        print(f"🌍 Country: {whois_data.get('country', 'N/A')}")
    else:
        print(f"❌ Investigation failed: {result.get('error')}")


async def handle_phone_recon(recon_engine):
    """Handle phone reconnaissance"""
    print("\n📱 Phone Number OSINT")
    print("-" * 30)
    
    phone = input("Enter phone number (with country code): ").strip()
    if not phone:
        print("❌ Phone number is required!")
        return
    
    print(f"\n🔍 Investigating phone number: {phone}")
    print("⏳ Please wait...")
    
    result = await recon_engine.run_phone_recon(phone)
    
    if result.get('success'):
        data = result.get('data', {})
        location = data.get('location', {})
        carrier_info = data.get('carrier', {})
        
        print(f"\n✅ Phone investigation completed!")
        print(f"📍 Country: {location.get('country', 'N/A')}")
        print(f"📡 Carrier: {carrier_info.get('name', 'N/A')}")
        print(f"📞 Type: {data.get('number_type', 'N/A')}")
        print(f"✅ Valid: {data.get('is_valid', False)}")
    else:
        print(f"❌ Investigation failed: {result.get('error')}")


async def handle_linkedin_recon(recon_engine):
    """Handle LinkedIn reconnaissance"""
    print("\n💼 LinkedIn Reconnaissance")
    print("-" * 30)
    
    first_name = input("Enter first name: ").strip()
    last_name = input("Enter last name: ").strip()
    
    if not first_name or not last_name:
        print("❌ Both first and last name are required!")
        return
    
    company = input("Enter company (optional): ").strip()
    location = input("Enter location (optional): ").strip()
    
    print(f"\n🔍 Searching LinkedIn for: {first_name} {last_name}")
    print("⏳ Please wait...")
    
    result = await recon_engine.run_linkedin_recon(
        first_name, last_name, company=company, location=location
    )
    
    if result.get('success'):
        data = result.get('data', {})
        search_urls = data.get('search_urls', [])
        
        print(f"\n✅ LinkedIn search completed!")
        print(f"🔗 Generated {len(search_urls)} search queries")
        print("🌐 Search URLs have been generated and browser opened (if configured)")
    else:
        print(f"❌ Investigation failed: {result.get('error')}")


async def handle_shodan_recon(recon_engine):
    """Handle Shodan reconnaissance"""
    print("\n🔍 Shodan Intelligence")
    print("-" * 30)
    
    target = input("Enter IP address or domain: ").strip()
    if not target:
        print("❌ Target is required!")
        return
    
    print(f"\n🔍 Investigating target: {target}")
    print("⏳ Please wait...")
    
    result = await recon_engine.run_shodan_recon(target)
    
    if result.get('success'):
        data = result.get('data', {})
        stats = data.get('statistics', {})
        
        print(f"\n✅ Shodan investigation completed!")
        if data.get('type') == 'ip':
            host_info = data.get('host_info', {})
            print(f"🌍 Country: {host_info.get('country_name', 'N/A')}")
            print(f"🏢 Organization: {host_info.get('organization', 'N/A')}")
            print(f"🔌 Open Ports: {len(host_info.get('ports', []))}")
            print(f"⚠️  Vulnerabilities: {len(host_info.get('vulns', []))}")
        else:
            print(f"🌐 IPs found: {stats.get('total_ips', 0)}")
            print(f"🔌 Total ports: {stats.get('total_ports', 0)}")
    else:
        print(f"❌ Investigation failed: {result.get('error')}")


async def handle_comprehensive_recon(recon_engine):
    """Handle comprehensive reconnaissance"""
    print("\n🎯 Comprehensive Reconnaissance")
    print("-" * 40)
    
    targets = {}
    
    github_user = input("GitHub username (optional): ").strip()
    if github_user:
        targets['github_username'] = github_user
    
    domain = input("Domain (optional): ").strip()
    if domain:
        targets['domain'] = domain
    
    phone = input("Phone number (optional): ").strip()
    if phone:
        targets['phone_number'] = phone
    
    linkedin_name = input("LinkedIn name (First Last, optional): ").strip()
    if linkedin_name:
        targets['linkedin_name'] = linkedin_name
    
    shodan_target = input("Shodan target (optional): ").strip()
    if shodan_target:
        targets['shodan_target'] = shodan_target
    
    if not targets:
        print("❌ At least one target is required!")
        return
    
    print(f"\n🔍 Running comprehensive reconnaissance...")
    print("⏳ This may take a while...")
    
    result = await recon_engine.run_comprehensive_recon(targets)
    
    if result.get('results'):
        summary = result.get('summary', {})
        print(f"\n✅ Comprehensive reconnaissance completed!")
        print(f"📊 Modules run: {summary.get('total_modules_run', 0)}")
        print(f"✅ Successful: {len(summary.get('successful_modules', []))}")
        print(f"❌ Failed: {len(summary.get('failed_modules', []))}")
        print(f"🔍 Key findings: {len(summary.get('key_findings', []))}")
    else:
        print(f"❌ Comprehensive reconnaissance failed")


def display_results(recon_engine):
    """Display current results"""
    print("\n📊 Current Results")
    print("-" * 30)
    
    results = recon_engine.get_results()
    
    if not results:
        print("📭 No results available. Run some investigations first!")
        return
    
    for module, result in results.items():
        status = "✅" if result.get('success') else "❌"
        timestamp = result.get('timestamp', 'N/A')
        print(f"{status} {module.upper()}: {timestamp}")


def display_configuration():
    """Display current configuration"""
    print("\n⚙️  Configuration")
    print("-" * 30)
    
    current_config = config.config
    
    # API Keys status
    print("🔑 API Keys:")
    api_keys = current_config.get('api_keys', {})
    for key, value in api_keys.items():
        status = "✅ Configured" if value else "❌ Not configured"
        print(f"  {key}: {status}")
    
    # Settings
    print("\n⚙️  Settings:")
    settings = current_config.get('settings', {})
    for key, value in settings.items():
        print(f"  {key}: {value}")


def display_module_status(recon_engine):
    """Display module status"""
    print("\n📋 Module Status")
    print("-" * 30)
    
    status = recon_engine.get_module_status()
    
    for module, is_configured in status.items():
        status_icon = "✅" if is_configured else "⚠️ "
        status_text = "Ready" if is_configured else "Needs configuration"
        print(f"{status_icon} {module.upper()}: {status_text}")


def run_web_mode():
    """Run in web mode"""
    print_banner()
    
    host = config.get("web_ui.host", "127.0.0.1")
    port = config.get("web_ui.port", 5000)
    debug = config.get("web_ui.debug", False)
    
    print(f"🌐 Starting xPOURY4 Recon Web UI...")
    print(f"🔗 URL: http://{host}:{port}")
    print(f"🔧 Debug mode: {'ON' if debug else 'OFF'}")
    print("📝 Press Ctrl+C to stop the server")
    
    try:
        app = create_app()
        app.socketio.run(app, host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n\n👋 Web server stopped.")
    except Exception as e:
        logger.error(f"Web server error: {e}")
        print(f"❌ Failed to start web server: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="xPOURY4 Recon - Elite Cyber Intelligence & Digital Forensics Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run in CLI mode
  python main.py --web             # Run web interface
  python main.py --config          # Show configuration
  python main.py --version         # Show version
        """
    )
    
    parser.add_argument(
        '--web', 
        action='store_true',
        help='Run web interface'
    )
    
    parser.add_argument(
        '--config',
        action='store_true', 
        help='Show configuration and exit'
    )
    
    parser.add_argument(
        '--version',
        action='store_true',
        help='Show version and exit'
    )
    
    args = parser.parse_args()
    
    if args.version:
        print("xPOURY4 Recon v1.0.0")
        print("Author: xPOURY4")
        return
    
    if args.config:
        display_configuration()
        return
    
    if args.web:
        run_web_mode()
    else:
        try:
            asyncio.run(run_cli_mode())
        except KeyboardInterrupt:
            print("\n\n👋 Thank you for using xPOURY4 Recon!")
        except Exception as e:
            logger.error(f"Application error: {e}")
            print(f"❌ Application error: {e}")


if __name__ == "__main__":
    main() 