import { redirect } from '@sveltejs/kit';
import { browser } from '$app/environment';
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async ({ url }) => {
   const token = browser ? localStorage.getItem('token') : null;

    const isPublicPage = url.pathname === '/auth/login' || url.pathname === '/auth/reg';
    
    if (browser) {
        if (!token && !isPublicPage) {
            throw redirect(307, '/auth/login');
        }

        if (token && isPublicPage) {
            throw redirect(307, '/products');
        }
    }

    return {
        token
    };
};