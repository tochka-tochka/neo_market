import type { PageLoad } from './$types';
import type { ProductType, SkuType } from '$lib/types';
import { API_URL } from '$lib';
import type { Category } from '$lib/types';

export const load: PageLoad = async ({ fetch }) => {
    try {
        const res = await fetch(`${API_URL}/categories/`, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
        }}).then(res => res.json());
        console.log(res)
        const categories : Category[] = res.categories
        return { "categories": categories };
    } catch (error) {
        console.error('Error fetching categories:', error);
        return { "categories": [] };
    }
};

