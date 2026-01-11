
import { HeroSection } from '@/components/blocks/hero-section-6';
import Nav from '../components/Nav';

export default function Signup() {
    return (
        <div className="min-h-screen bg-background">
            <Nav />
            {/* Adjusting top padding because Nav is fixed */}
            <div className="">
                <HeroSection />
            </div>
        </div>
    );
}
