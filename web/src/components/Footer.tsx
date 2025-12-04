import React from 'react';

import { Github, Linkedin } from 'lucide-react';

export default function Footer() {
    const currentYear = new Date().getFullYear();

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
                            <SocialLink href="https://github.com/zimaxnet/secai-radar" icon={Github} label="GitHub" />
                            <SocialLink href="https://linkedin.com/in/derekbmoore" icon={Linkedin} label="LinkedIn" />
                        </div>
                    </div>

                    {/* Product Column */}
                    <div>
                        <h3 className="text-white font-semibold mb-6">Product</h3>
                        <ul className="space-y-3 text-sm">
                            <FooterLink href="#features">Features</FooterLink>
                            <FooterLink href="#how-it-works">How it Works</FooterLink>
                            <FooterLink href="#">Security Domains</FooterLink>
                            <FooterLink href="#">Pricing</FooterLink>
                            <FooterLink href="#">Enterprise</FooterLink>
                        </ul>
                    </div>

                    {/* Resources Column */}
                    <div>
                        <h3 className="text-white font-semibold mb-6">Resources</h3>
                        <ul className="space-y-3 text-sm">
                            <FooterLink href="https://wiki.secairadar.cloud" external>Documentation</FooterLink>
                            <FooterLink href="#">API Reference</FooterLink>
                            <FooterLink href="#">Blog</FooterLink>
                            <FooterLink href="#">Community</FooterLink>
                            <FooterLink href="#">Security Guide</FooterLink>
                        </ul>
                    </div>

                    {/* Company Column */}
                    <div>
                        <h3 className="text-white font-semibold mb-6">Company</h3>
                        <ul className="space-y-3 text-sm">
                            <FooterLink href="#">About Us</FooterLink>
                            <FooterLink href="#">Careers</FooterLink>
                            <FooterLink href="#">Legal</FooterLink>
                            <FooterLink href="#">Privacy Policy</FooterLink>
                            <FooterLink href="#">Contact</FooterLink>
                        </ul>
                    </div>
                </div>

                {/* Bottom Bar */}
                <div className="pt-8 border-t border-slate-900 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-slate-600">
                    <div>
                        &copy; {currentYear} SecAI Radar. All rights reserved.
                    </div>
                    <div className="flex gap-8">
                        <a href="#" className="hover:text-slate-400 transition-colors">Privacy</a>
                        <a href="#" className="hover:text-slate-400 transition-colors">Terms</a>
                        <a href="#" className="hover:text-slate-400 transition-colors">Cookies</a>
                    </div>
                </div>
            </div>
        </footer>
    );
}

function SocialLink({ href, icon: Icon, label }: { href: string; icon: React.ElementType; label: string }) {
    return (
        <a
            href={href}
            className="w-8 h-8 rounded-full bg-slate-900 flex items-center justify-center hover:bg-blue-600 hover:text-white transition-all duration-300"
            aria-label={label}
        >
            <Icon className="w-4 h-4" />
        </a>
    );
}

function FooterLink({ href, children, external }: { href: string; children: React.ReactNode; external?: boolean }) {
    return (
        <li>
            <a
                href={href}
                target={external ? "_blank" : undefined}
                rel={external ? "noopener noreferrer" : undefined}
                className="hover:text-blue-400 transition-colors flex items-center gap-1"
            >
                {children}
            </a>
        </li>
    );
}
function XIcon({ className }: { className?: string }) {
    return (
        <svg viewBox="0 0 24 24" aria-hidden="true" className={className} fill="currentColor">
            <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
        </svg>
    );
}
