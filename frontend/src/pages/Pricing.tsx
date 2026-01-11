
"use client";

import { Pricing as PricingBlock } from "@/components/blocks/pricing";
import Nav from "@/components/Nav";

const demoPlans = [
    {
        name: "STARTER",
        price: "0",
        yearlyPrice: "0",
        period: "forever",
        features: [
            "Access to public destinations",
            "Basic AI trip planning",
            "Community support",
            "Ad-supported experience",
        ],
        description: "Perfect for casual travelers",
        buttonText: "Start Free",
        href: "/signup?plan=starter",
        isPopular: false,
    },
    {
        name: "EXPLORER",
        price: "9.99",
        yearlyPrice: "7.99",
        period: "per month",
        features: [
            "Unlimited AI trip generation",
            "Exclusive hidden gems",
            "Ad-free experience",
            "Priority support",
            "Offline maps access",
            "Advanced filtering",
        ],
        description: "Ideal for frequent travelers",
        buttonText: "Get Started",
        href: "/checkout?type=Subscription&name=Explorer Plan&price=9.99&plan=explorer",
        isPopular: true,
    },
    {
        name: "WORLD CLASS",
        price: "19.99",
        yearlyPrice: "15.99",
        period: "per month",
        features: [
            "Everything in Explorer",
            "Personal travel concierge",
            "VIP hotel perks",
            "Global lounge access discount",
            "Travel insurance tracking",
            "dedicated account manager",
        ],
        description: "For the ultimate luxury experience",
        buttonText: "Join VIP",
        href: "/checkout?type=Subscription&name=World Class Plan&price=19.99&plan=world-class",
        isPopular: false,
    },
];

export default function PricingPage() {
    return (
        <div className="min-h-screen bg-background text-foreground">
            <Nav />
            <div className="pt-24 pb-12">
                <PricingBlock
                    plans={demoPlans}
                    title="Simple, Transparent Pricing"
                    description={"Choose the plan that works for you\nAll plans include access to our platform, lead generation tools, and dedicated support."}
                />
            </div>
        </div>
    );
}
