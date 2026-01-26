import { SocialLink, FooterLink, XIcon, GithubIcon, LinkedinIcon } from './FooterHelpers';

export default function Footer(): JSX.Element {
    return (
        <footer className="bg-slate-950 border-t border-slate-800 pt-16 pb-8 text-slate-400 font-sans">
            <div className="container mx-auto px-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-16">
                    {/* Brand Column */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-2 text-white">
                            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-cyan-400 rounded-lg flex items-center justify-center font-bold shadow-lg shadow-blue-500/20">
                                S
                            </div>
                            <span className="text-xl font-bold tracking-tight">SecAI Radar</span>
                        </div>
                        <p className="text-sm leading-relaxed text-slate-500 max-w-xs">
                            The vendor-neutral security assessment platform for the AI era. Visualize, analyze, and secure your cloud infrastructure with confidence.
                        </p>
                        <div className="flex gap-4 pt-2">
                            <SocialLink href="https://x.com/zimaxnet" icon={XIcon} label="X (Twitter)" />
                            <SocialLink href="https://github.com/zimaxnet/secai-radar" icon={GithubIcon} label="GitHub" />
                            <SocialLink href="https://linkedin.com/in/derekbmoore" icon={LinkedinIcon} label="LinkedIn" />
                        </div>
                    </div>

                    {/* Product Column */}
                    <div>
                        <h3 className="text-white font-semibold mb-6">Product</h3>
                        <ul className="space-y-3 text-sm">
                            <FooterLink href="#features">Features</FooterLink>
                            <FooterLink href="#how-it-works">How it Works</FooterLink>
                            <FooterLink href="/">Security Domains</FooterLink>
                            <FooterLink href="/">Pricing</FooterLink>
                            <FooterLink href="/">Enterprise</FooterLink>
                        </ul>
                    </div>

                    {/* Resources Column */}
                    <div>
                        <h3 className="text-white font-semibold mb-6">Resources</h3>
                        <ul className="space-y-3 text-sm">
                            <FooterLink href="https://wiki.secairadar.cloud" external>Documentation</FooterLink>
                            <FooterLink href="/">API Reference</FooterLink>
                            <FooterLink href="/">Blog</FooterLink>
                            <FooterLink href="/">Community</FooterLink>
                            <FooterLink href="/">Security Guide</FooterLink>
                        </ul>
                    </div>

                    {/* Company Column */}
                    <div>
                        <h3 className="text-white font-semibold mb-6">Company</h3>
                        <ul className="space-y-3 text-sm">
                            <FooterLink href="/">About Us</FooterLink>
                            <FooterLink href="/">Careers</FooterLink>
                            <FooterLink href="/">Legal</FooterLink>
                            <FooterLink href="/">Privacy Policy</FooterLink>
                            <FooterLink href="/">Contact</FooterLink>
                        </ul>
                    </div>
                </div>

                {/* Bottom Bar */}
                <div className="pt-8 border-t border-slate-900 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-slate-600">
                    <div>
                        &copy; {new Date().getFullYear()} SecAI Radar. All rights reserved.
                    </div>
                    <div className="flex gap-8">
                        <a href="/" className="hover:text-slate-400 transition-colors">Privacy</a>
                        <a href="/" className="hover:text-slate-400 transition-colors">Terms</a>
                        <a href="/" className="hover:text-slate-400 transition-colors">Cookies</a>
                    </div>
                </div>
            </div>
        </footer>
    );
}
