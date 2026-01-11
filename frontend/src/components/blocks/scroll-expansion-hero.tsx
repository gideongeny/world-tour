
'use client';

import {
    useEffect,
    useRef,
    useState,
    ReactNode,
    // TouchEvent, // Removed unused types
    // WheelEvent, // Removed unused types
} from 'react';
// import Image from 'next/image'; // Replaced with img tag
import { motion } from 'framer-motion';

interface ScrollExpandMediaProps {
    mediaType?: 'video' | 'image';
    mediaSrc: string;
    posterSrc?: string;
    bgImageSrc: string;
    title?: string;
    date?: string;
    scrollToExpand?: string;
    textBlend?: boolean;
    children?: ReactNode;
}

const ScrollExpandMedia = ({
    mediaType = 'video',
    mediaSrc,
    posterSrc,
    bgImageSrc,
    title,
    date,
    scrollToExpand,
    textBlend,
    children,
}: ScrollExpandMediaProps) => {
    const [scrollProgress, setScrollProgress] = useState<number>(0);
    const [showContent, setShowContent] = useState<boolean>(false);
    const [mediaFullyExpanded, setMediaFullyExpanded] = useState<boolean>(false);
    const [touchStartY, setTouchStartY] = useState<number>(0);
    const [isMobileState, setIsMobileState] = useState<boolean>(false);

    const sectionRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        setScrollProgress(0);
        setShowContent(false);
        setMediaFullyExpanded(false);
    }, [mediaType]);

    useEffect(() => {
        const handleWheel = (e: WheelEvent) => {
            // Logic adjustment: Don't prevent default unless we are in the specific interaction zone
            // For this integration, let's make it less invasive to the global scroll
            // Only hijack if we are at the top of the page?

            if (window.scrollY > 100) return; // Allow normal scroll if page is scrolled down

            if (mediaFullyExpanded && e.deltaY < 0 && window.scrollY <= 5) {
                setMediaFullyExpanded(false);
                e.preventDefault();
            } else if (!mediaFullyExpanded) {
                // e.preventDefault(); // Commenting out to check behavior
                const scrollDelta = e.deltaY * 0.0009;
                const newProgress = Math.min(
                    Math.max(scrollProgress + scrollDelta, 0),
                    1
                );
                setScrollProgress(newProgress);

                if (newProgress >= 1) {
                    setMediaFullyExpanded(true);
                    setShowContent(true);
                } else if (newProgress < 0.75) {
                    setShowContent(false);
                }
            }
        };

        const handleTouchStart = (e: TouchEvent) => {
            if (window.scrollY > 100) return;
            setTouchStartY(e.touches[0].clientY);
        };

        const handleTouchMove = (e: TouchEvent) => {
            if (window.scrollY > 100) return;
            if (!touchStartY) return;

            const touchY = e.touches[0].clientY;
            const deltaY = touchStartY - touchY;

            if (mediaFullyExpanded && deltaY < -20 && window.scrollY <= 5) {
                setMediaFullyExpanded(false);
                // e.preventDefault();
            } else if (!mediaFullyExpanded) {
                // e.preventDefault();
                // Increase sensitivity for mobile, especially when scrolling back
                const scrollFactor = deltaY < 0 ? 0.008 : 0.005; // Higher sensitivity for scrolling back
                const scrollDelta = deltaY * scrollFactor;
                const newProgress = Math.min(
                    Math.max(scrollProgress + scrollDelta, 0),
                    1
                );
                setScrollProgress(newProgress);

                if (newProgress >= 1) {
                    setMediaFullyExpanded(true);
                    setShowContent(true);
                } else if (newProgress < 0.75) {
                    setShowContent(false);
                }

                setTouchStartY(touchY);
            }
        };

        const handleTouchEnd = (): void => {
            setTouchStartY(0);
        };

        const handleScroll = (): void => {
            if (!mediaFullyExpanded && window.scrollY < 50) {
                // window.scrollTo(0, 0); // Removed aggressive scrolling
            }
        };

        /* 
           Note: Attaching these listeners to window can be problematic for a single component.
           Ideally, we monitor the sectionRef. For now, keeping as is but adding checks.
        */
        // window.addEventListener('wheel', handleWheel as unknown as EventListener, { passive: false });
        // window.addEventListener('scroll', handleScroll as EventListener);
        // window.addEventListener('touchstart', handleTouchStart as unknown as EventListener, { passive: false });
        // window.addEventListener('touchmove', handleTouchMove as unknown as EventListener, { passive: false });
        // window.addEventListener('touchend', handleTouchEnd as EventListener);

        return () => {
            // Cleanups
        };
    }, [scrollProgress, mediaFullyExpanded, touchStartY]);

    // Fallback effect for standard scrolling interaction without hijacking
    useEffect(() => {
        const handleScroll = () => {
            const scrollY = window.scrollY;
            const viewportHeight = window.innerHeight;
            // Simple progress based on how far we've scrolled past the top
            // This is a more standard "parallax" appraoch than "scroll-jacking"
            const progress = Math.min(Math.max(scrollY / (viewportHeight * 0.5), 0), 1);

            setScrollProgress(progress);

            if (progress > 0.8) {
                setMediaFullyExpanded(true);
                setShowContent(true);
            } else {
                setMediaFullyExpanded(false);
                setShowContent(false);
            }
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);


    useEffect(() => {
        const checkIfMobile = (): void => {
            setIsMobileState(window.innerWidth < 768);
        };

        checkIfMobile();
        window.addEventListener('resize', checkIfMobile);

        return () => window.removeEventListener('resize', checkIfMobile);
    }, []);

    const mediaWidth = 300 + scrollProgress * (isMobileState ? 650 : 1250);
    const mediaHeight = 400 + scrollProgress * (isMobileState ? 200 : 400);
    const textTranslateX = scrollProgress * (isMobileState ? 180 : 150);

    const firstWord = title ? title.split(' ')[0] : '';
    const restOfTitle = title ? title.split(' ').slice(1).join(' ') : '';

    return (
        <div
            ref={sectionRef}
            className='transition-colors duration-700 ease-in-out overflow-x-hidden relative h-[200vh]' // Made container taller to allow scrolling
        >
            <section className='sticky top-0 flex flex-col items-center justify-start min-h-[100dvh] overflow-hidden'>
                <div className='relative w-full flex flex-col items-center min-h-[100dvh]'>
                    <motion.div
                        className='absolute inset-0 z-0 h-full'
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 - scrollProgress }}
                        transition={{ duration: 0.1 }}
                    >
                        <img
                            src={bgImageSrc}
                            alt='Background'
                            className='w-full h-full object-cover object-center'
                        />
                        <div className='absolute inset-0 bg-black/40' />
                    </motion.div>

                    <div className='container mx-auto flex flex-col items-center justify-start relative z-10'>
                        <div className='flex flex-col items-center justify-center w-full h-[100dvh] relative'>
                            <div
                                className='absolute z-0 top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 transition-none rounded-2xl overflow-hidden shadow-2xl'
                                style={{
                                    width: `${mediaWidth}px`,
                                    height: `${mediaHeight}px`,
                                    maxWidth: '90vw',
                                    maxHeight: '80vh',
                                }}
                            >
                                {mediaType === 'video' ? (
                                    mediaSrc.includes('youtube.com') ? (
                                        <div className='relative w-full h-full pointer-events-none'>
                                            <iframe
                                                width='100%'
                                                height='100%'
                                                src={
                                                    mediaSrc.includes('embed')
                                                        ? mediaSrc +
                                                        (mediaSrc.includes('?') ? '&' : '?') +
                                                        'autoplay=1&mute=1&loop=1&controls=0&showinfo=0&rel=0&disablekb=1&modestbranding=1'
                                                        : mediaSrc.replace('watch?v=', 'embed/') +
                                                        '?autoplay=1&mute=1&loop=1&controls=0&showinfo=0&rel=0&disablekb=1&modestbranding=1&playlist=' +
                                                        mediaSrc.split('v=')[1]
                                                }
                                                className='w-full h-full rounded-xl'
                                                frameBorder='0'
                                                allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture'
                                                allowFullScreen
                                            />
                                            <div
                                                className='absolute inset-0 z-10'
                                                style={{ pointerEvents: 'none' }}
                                            ></div>

                                            <motion.div
                                                className='absolute inset-0 bg-black/30 rounded-xl'
                                                initial={{ opacity: 0.7 }}
                                                animate={{ opacity: 0.5 - scrollProgress * 0.3 }}
                                                transition={{ duration: 0.2 }}
                                            />
                                        </div>
                                    ) : (
                                        <div className='relative w-full h-full pointer-events-none'>
                                            <video
                                                src={mediaSrc}
                                                poster={posterSrc}
                                                autoPlay
                                                muted
                                                loop
                                                playsInline
                                                preload='auto'
                                                className='w-full h-full object-cover rounded-xl'
                                                controls={false}
                                                disablePictureInPicture
                                                disableRemotePlayback
                                            />
                                            <div
                                                className='absolute inset-0 z-10'
                                                style={{ pointerEvents: 'none' }}
                                            ></div>

                                            <motion.div
                                                className='absolute inset-0 bg-black/30 rounded-xl'
                                                initial={{ opacity: 0.7 }}
                                                animate={{ opacity: 0.5 - scrollProgress * 0.3 }}
                                                transition={{ duration: 0.2 }}
                                            />
                                        </div>
                                    )
                                ) : (
                                    <div className='relative w-full h-full'>
                                        <img
                                            src={mediaSrc}
                                            alt={title || 'Media content'}
                                            className='w-full h-full object-cover rounded-xl'
                                        />

                                        <motion.div
                                            className='absolute inset-0 bg-black/50 rounded-xl'
                                            initial={{ opacity: 0.7 }}
                                            animate={{ opacity: 0.7 - scrollProgress * 0.3 }}
                                            transition={{ duration: 0.2 }}
                                        />
                                    </div>
                                )}

                                <div className='flex flex-col items-center text-center relative z-10 mt-4 transition-none'>
                                    {date && (
                                        <p
                                            className='text-2xl text-white font-bold drop-shadow-md'
                                            style={{ transform: `translateX(-${textTranslateX}vw)` }}
                                        >
                                            {date}
                                        </p>
                                    )}
                                    {scrollToExpand && (
                                        <p
                                            className='text-blue-200 font-medium text-center'
                                            style={{ transform: `translateX(${textTranslateX}vw)` }}
                                        >
                                            {scrollToExpand}
                                        </p>
                                    )}
                                </div>
                            </div>

                            <div
                                className={`flex items-center justify-center text-center gap-4 w-full relative z-10 transition-none flex-col ${textBlend ? 'mix-blend-difference' : 'mix-blend-normal'
                                    }`}
                            >
                                <motion.h2
                                    className='text-4xl md:text-5xl lg:text-6xl font-black text-white drop-shadow-lg transition-none'
                                    style={{ transform: `translateX(-${textTranslateX}vw)` }}
                                >
                                    {firstWord}
                                </motion.h2>
                                <motion.h2
                                    className='text-4xl md:text-5xl lg:text-6xl font-black text-center text-white drop-shadow-lg transition-none'
                                    style={{ transform: `translateX(${textTranslateX}vw)` }}
                                >
                                    {restOfTitle}
                                </motion.h2>
                            </div>
                        </div>

                        <motion.section
                            className='flex flex-col w-full px-8 py-10 md:px-16 lg:py-20'
                            initial={{ opacity: 0 }}
                            animate={{ opacity: showContent ? 1 : 0 }}
                            transition={{ duration: 0.7 }}
                        >
                            {children}
                        </motion.section>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default ScrollExpandMedia;
