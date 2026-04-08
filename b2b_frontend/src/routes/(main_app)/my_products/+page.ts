import type { PageLoad } from './$types';
import type { ProductType, Char } from '$lib/types';
import { API_URL } from '$lib';

export const load: PageLoad = async ({ fetch }) => {
    try {
        const res = await fetch(`${API_URL}/products/my/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
        }}).then(res => res.json());
        const products : ProductType[] = res.products;
        return { "products": products ?? [] };
    } catch (error) {
        console.error('Error fetching products:', error);
        return { "products": [] }; 
    }
};