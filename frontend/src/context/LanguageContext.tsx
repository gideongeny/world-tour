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
        'home.destinations.title': 'World Class Destinations',
        'home.map.title': 'Explore the Map',
        'home.cta.title': 'Ready for your next adventure?',
        'hotels.hero.title': 'Luxury Stays',
        'hotels.search.destination': 'Destination',
        'hotels.search.dates': 'Dates',
        'hotels.search.currency': 'Currency',
        'hotels.search.placeholder': 'Where are you going?',
        'common.view_all': 'View All',
        'common.get_started': 'Get Started',
        'common.contact_sales': 'Contact Sales'
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
        'home.destinations.title': 'Destinations de Classe Mondiale',
        'home.map.title': 'Explorer la Carte',
        'home.cta.title': 'Prêt pour votre prochaine aventure ?',
        'hotels.hero.title': 'Séjours de Luxe',
        'hotels.search.destination': 'Destination',
        'hotels.search.dates': 'Dates',
        'hotels.search.currency': 'Devise',
        'hotels.search.placeholder': 'Où allez-vous ?',
        'common.view_all': 'Voir Tout',
        'common.get_started': 'Commencer',
        'common.contact_sales': 'Contacter les Ventes'
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
        'home.destinations.title': 'Vitoe vya Hadhi ya Dunia',
        'home.map.title': 'Chunguza Ramani',
        'home.cta.title': 'Uko tayari kwa safari yako ijayo?',
        'hotels.hero.title': 'Malazi ya Kifahari',
        'hotels.search.destination': 'Kitoe',
        'hotels.search.dates': 'Tarehe',
        'hotels.search.currency': 'Sarafu',
        'hotels.search.placeholder': 'Unaenda wapi?',
        'common.view_all': 'Ona Zote',
        'common.get_started': 'Anza Sasa',
        'common.contact_sales': 'Wasiliana na Mauzo'
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
        'home.destinations.title': 'Destinos de Clase Mundial',
        'home.map.title': 'Explorar el Mapa',
        'home.cta.title': '¿Listo para tu próxima aventura?',
        'hotels.hero.title': 'Estancias de Lujo',
        'hotels.search.destination': 'Destino',
        'hotels.search.dates': 'Fechas',
        'hotels.search.currency': 'Moneda',
        'hotels.search.placeholder': '¿A dónde vas?',
        'common.view_all': 'Ver Todo',
        'common.get_started': 'Empezar',
        'common.contact_sales': 'Contactar Ventas'
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
        'home.destinations.title': '世界级目的地',
        'home.map.title': '探索地图',
        'home.cta.title': '准备好下一次冒险了吗？',
        'hotels.hero.title': '豪华住宿',
        'hotels.search.destination': '目的地',
        'hotels.search.dates': '日期',
        'hotels.search.currency': '货币',
        'hotels.search.placeholder': '你要去哪里？',
        'common.view_all': '查看全部',
        'common.get_started': '开始',
        'common.contact_sales': '联系销售'
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
        'home.destinations.title': 'وجهات عالمية المستوى',
        'home.map.title': 'اكتشف الخريطة',
        'home.cta.title': 'هل أنت مستعد لمغامرتك القادمة؟',
        'hotels.hero.title': 'إقامات فاخرة',
        'hotels.search.destination': 'الوجهة',
        'hotels.search.dates': 'التواريخ',
        'hotels.search.currency': 'العملة',
        'hotels.search.placeholder': 'إلى أين تذهب؟',
        'common.view_all': 'عرض الكل',
        'common.get_started': 'البدء',
        'common.contact_sales': 'اتصل بالمبيعات'
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
