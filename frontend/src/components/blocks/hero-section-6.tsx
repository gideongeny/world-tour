
'use client'
import { Button } from '@/components/ui/button'
import { ArrowRight, Mail, Menu, SendHorizonal, X } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useState } from 'react'
import { cn } from '@/lib/utils'

const menuItems = [
    { name: 'Home', href: '/' },
    { name: 'Hotels', href: '/hotels' },
    { name: 'Flights', href: '/flights' },
    { name: 'Pricing', href: '/pricing' },
]

export function HeroSection() {
    const [menuState, setMenuState] = useState(false)
    return (
        <>
            <main>
                <section className="overflow-hidden">
                    <div className="relative mx-auto max-w-5xl px-6 py-28 lg:py-20">
                        <div className="lg:flex lg:items-center lg:gap-12">
                            <div className="relative z-10 mx-auto max-w-xl text-center lg:ml-0 lg:w-1/2 lg:text-left">
                                <Link
                                    to="/"
                                    className="rounded-lg mx-auto flex w-fit items-center gap-2 border p-1 pr-3 lg:ml-0">
                                    <span className="bg-muted rounded-[calc(var(--radius)-0.25rem)] px-2 py-1 text-xs bg-slate-100 dark:bg-slate-800">New</span>
                                    <span className="text-sm">Join World Tour Premium</span>
                                    <span className="bg-(--color-border) block h-4 w-px"></span>

                                    <ArrowRight className="size-4" />
                                </Link>

                                <h1 className="mt-10 text-balance text-4xl font-bold md:text-5xl xl:text-5xl">Explore the World Like Never Before</h1>
                                <p className="mt-8 text-slate-600 dark:text-slate-300">Unlock exclusive travel deals, AI-powered itineraries, and premium support. Your next adventure awaits.</p>

                                <div>
                                    <form
                                        action=""
                                        className="mx-auto my-10 max-w-sm lg:my-12 lg:ml-0 lg:mr-auto">
                                        <div className="bg-background has-[input:focus]:ring-muted relative grid grid-cols-[1fr_auto] items-center rounded-[1rem] border pr-1 shadow shadow-zinc-950/5 has-[input:focus]:ring-2">
                                            <Mail className="text-caption pointer-events-none absolute inset-y-0 left-5 my-auto size-5 text-gray-400" />

                                            <input
                                                placeholder="Your mail address"
                                                className="h-14 w-full bg-transparent pl-12 focus:outline-none"
                                                type="email"
                                            />

                                            <div className="md:pr-1.5 lg:pr-0">
                                                <Button
                                                    aria-label="submit"
                                                >
                                                    <span className="hidden md:block">Get Started</span>
                                                    <SendHorizonal
                                                        className="relative mx-auto size-5 md:hidden"
                                                        strokeWidth={2}
                                                    />
                                                </Button>
                                            </div>
                                        </div>
                                    </form>

                                    <ul className="list-inside list-disc space-y-2 text-slate-600 dark:text-slate-300">
                                        <li>Smart AI Planning</li>
                                        <li>Exclusive Hotel Deals</li>
                                        <li>24/7 Premium Support</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        <div className="absolute inset-0 -mx-4 rounded-3xl p-3 lg:col-span-3">
                            <div aria-hidden className="absolute z-[1] inset-0 bg-gradient-to-r from-background from-35%" />
                            <div className="relative h-full w-full opacity-30 lg:opacity-100">
                                {/* Using Unsplash image instead of missing tailark assets */}
                                <img
                                    className="hidden dark:block object-cover w-full h-full rounded-3xl"
                                    src="https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=1200&q=80"
                                    alt="app illustration"
                                />
                                <img
                                    className="dark:hidden object-cover w-full h-full rounded-3xl"
                                    src="https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1200&q=80"
                                    alt="app illustration"
                                />
                            </div>
                        </div>
                    </div>
                </section>
            </main>
        </>
    )
}

const Logo = ({ className }: { className?: string }) => {
    return (
        <svg
            viewBox="0 0 78 18"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className={cn('h-5 w-auto', className)}>
            <path
                d="M3 0H5V18H3V0ZM13 0H15V18H13V0ZM18 3V5H0V3H18ZM0 15V13H18V15H0Z"
                fill="url(#logo-gradient)"
            />
            {/* SVG paths truncated for brevity in this manual create, assuming original from prompt is good or I can just use text logo */}
            <text x="25" y="14" fontSize="14" fontWeight="bold" fill="currentColor" fontFamily="sans-serif">World Tour</text>
            <defs>
                <linearGradient
                    id="logo-gradient"
                    x1="10"
                    y1="0"
                    x2="10"
                    y2="20"
                    gradientUnits="userSpaceOnUse">
                    <stop stopColor="#EA863A" />
                    <stop
                        offset="1"
                        stopColor="#2F5233"
                    />
                </linearGradient>
            </defs>
        </svg>
    )
}
