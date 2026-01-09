import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';

type Language = 'en' | 'fr' | 'sw' | 'es' | 'zh' | 'ar';

interface LanguageContextType {
    language: Language;
    setLanguage: (lang: Language) => void;
    t: (key: string) => string;
}

const translations: Record<Language, Record<string, string>> = {
    en: {
        'nav.destinations': 'Destinations',
        'nav.hotels': 'Hotels',
        'nav.flights': 'Flights',
        'nav.ai_assistant': 'AI Assistant',
        'nav.login': 'Login',
        'hero.subtitle': 'Hand-picked by our experts for your next adventure',
        'btn.book': 'Book Experience',
        'btn.search': 'Search',
    },
    fr: {
        'nav.destinations': 'Destinations',
        'nav.hotels': 'Hôtels',
        'nav.flights': 'Vols',
        'nav.ai_assistant': 'Assistant IA',
        'nav.login': 'Connexion',
        'hero.subtitle': 'Sélectionné par nos experts pour votre prochaine aventure',
        'btn.book': 'Réserver',
        'btn.search': 'Rechercher',
    },
    sw: {
        'nav.destinations': 'Vitoe',
        'nav.hotels': 'Hoteli',
        'nav.flights': 'Ndege',
        'nav.ai_assistant': 'Msaidizi wa AI',
        'nav.login': 'Ingia',
        'hero.subtitle': 'Imechaguliwa na wataalam wetu kwa safari yako ijayo',
        'btn.book': 'Weka Nafasi',
        'btn.search': 'Tafuta',
    },
    es: {
        'nav.destinations': 'Destinos',
        'nav.hotels': 'Hoteles',
        'nav.flights': 'Vuelos',
        'nav.ai_assistant': 'Asistente IA',
        'nav.login': 'Entrar',
        'hero.subtitle': 'Seleccionado por nuestros expertos para tu próxima aventura',
        'btn.book': 'Reservar',
        'btn.search': 'Buscar',
    },
    zh: {
        'nav.destinations': '目的地',
        'nav.hotels': '酒店',
        'nav.flights': '航班',
        'nav.ai_assistant': 'AI 助手',
        'nav.login': '登录',
        'hero.subtitle': '由我们的专家为您挑选的下一次冒险',
        'btn.book': '预订体验',
        'btn.search': '搜索',
    },
    ar: {
        'nav.destinations': 'الوجهات',
        'nav.hotels': 'فنادق',
        'nav.flights': 'رحلات طيران',
        'nav.ai_assistant': 'مساعد الذكاء الاصطناعي',
        'nav.login': 'تسجيل الدخول',
        'hero.subtitle': 'تم اختيارها بعناية من قبل خبرائنا لمغامرتك القادمة',
        'btn.book': 'احجز التجربة',
        'btn.search': 'يتحرى',
    }
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider = ({ children }: { children: ReactNode }) => {
    const [language, setLanguage] = useState<Language>('en');

    const t = (key: string) => {
        return translations[language][key] || key;
    };

    return (
        <LanguageContext.Provider value={{ language, setLanguage, t }}>
            {children}
        </LanguageContext.Provider>
    );
};

export const useLanguage = () => {
    const context = useContext(LanguageContext);
    if (context === undefined) {
        throw new Error('useLanguage must be used within a LanguageProvider');
    }
    return context;
};
