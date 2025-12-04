import { ElementType, ReactNode } from 'react';

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

interface SocialLinkProps {
    href: string;
    icon: ElementType;
    label: string;
}

function SocialLink({ href, icon: Icon, label }: SocialLinkProps): JSX.Element {
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

interface FooterLinkProps {
    href: string;
    children: ReactNode;
    external?: boolean;
}

function FooterLink({ href, children, external }: FooterLinkProps): JSX.Element {
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

function XIcon({ className }: { className?: string }): JSX.Element {
    return (
        <svg viewBox="0 0 24 24" aria-hidden="true" className={className} fill="currentColor">
            <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
        </svg>
    );
}

function GithubIcon({ className }: { className?: string }): JSX.Element {
    return (
        <svg viewBox="0 0 24 24" aria-hidden="true" className={className} fill="currentColor">
            <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
        </svg>
    );
}

function LinkedinIcon({ className }: { className?: string }): JSX.Element {
    return (
        <svg viewBox="0 0 24 24" aria-hidden="true" className={className} fill="currentColor">
            <path fillRule="evenodd" clipRule="evenodd" d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452z" />
        </svg>
    );
}
