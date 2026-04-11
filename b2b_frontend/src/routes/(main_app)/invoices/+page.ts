import type { PageLoad } from './$types';
import type { InvoiceType, ProductType, Char } from '$lib/types';
import { API_URL } from '$lib';

export const load: PageLoad = async ({ fetch }) => {
    try {
        const res = await fetch(`${API_URL}/products/my/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
        }}).then(res => res.json());
        const products : ProductType[] = res.products;
        // const res = await fetch(`${API_URL}/invoices/my/`, {
        //     headers: {
        //         'Authorization': `Bearer ${localStorage.getItem('token')}`
        // }}).then(res => res.json());
        // const invoices : InvoiceType[] = res.invoices;
        const invoices : InvoiceType[] = [
            {
                id: "11111111-1111-1111-1111-111111111111",
                items: [
                    {
                        product: {
                            id: "11111111-1111-1111-1111-111111111111",
                            title: "Product 1",
                            description: "Description of Product 1",
                            category: {
                                id: "11111111-1111-1111-1111-111111111111",
                                value: "Category 1"
                            },
                            status: "active",
                            characteristics: [
                                { name: "Brand", value: "Apple" },
                            ],
                            images: [
                                { id: "11111111-1111-1111-1111-111111111111", url: "https://example.com/image1.jpg", order: 1 },
                                { id: "11111111-1111-1111-1111-111111111111", url: "https://example.com/image1.jpg", order: 2 },
                                { id: "11111111-1111-1111-1111-111111111111", url: "https://example.com/image1.jpg", order: 3 },
                            ],
                            skus: [
                                {
                                    id: "11111111-1111-1111-1111-111111111111",
                                    name: "SKU 1",
                                    characteristics: [
                                        { name: "Color", value: "Red" },
                                        { name: "Size", value: "M" },
                                    ],
                                    price: 100,
                                    quantity: 10
                                }
                            ]
                        },
                        skuId: "11111111-1111-1111-1111-111111111111",
                        quantity: 2,
                    },
                    {
                        product: {
                            id: "22222222-2222-2222-2222-222222222222",
                            title: "Product 2",
                            description: "Description of Product 2",
                            category: {
                                id: "22222222-2222-2222-2222-222222222222",
                                value: "Category 1"
                            },
                            status: "active",
                            characteristics: [
                                { name: "Brand", value: "Apple" },
                            ],
                            images: [
                                { id: "22222222-2222-2222-2222-222222222222", url: "https://example.com/image1.jpg", order: 1 },
                                { id: "22222222-2222-2222-2222-222222222222", url: "https://example.com/image1.jpg", order: 2 },
                                { id: "22222222-2222-2222-2222-222222222222", url: "https://example.com/image1.jpg", order: 3 },
                            ],
                            skus: [
                                {
                                    id: "22222222-2222-2222-2222-222222222222",
                                    name: "SKU 1",
                                    characteristics: [
                                        { name: "Color", value: "Red" },
                                        { name: "Size", value: "M" },
                                    ],
                                    price: 100,
                                    quantity: 10
                                }
                            ]
                        },
                        skuId: "22222222-2222-2222-2222-222222222222",
                        quantity: 5,
                    },
                ],
                date: new Date(),
            }
        ];
        return { "invoices": invoices ?? [] };
    } catch (error) {
        console.error('Error fetching invoices:', error);
        return { "invoices": [] }; 
    }
};