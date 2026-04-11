import { API_URL } from '$lib';
import type { ProductType, SkuType, Char } from '$lib/types/index.js';

export const load = async ({ params }) => {
    try {
        const res = await fetch(`${API_URL}/products/${params.product_id}`,{
            method: "GET",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("token")}`,
            },
        }).then(res => res.json());
        const product : ProductType = res.product;

        product.skus = [
                        {
                            id: "1",
                            name: "256GB BLACK",
                            characteristics: [
                                {
                                    name: "Цвет",
                                    value: "Черный"
                                },
                                {
                                    name: "Память",
                                    value: "256GB"
                                }
                            ] as Char[],
                            price: 40000,
                            quantity: 23
                        },
                        {
                            id: "2",
                            name: "256GB WHITE",
                            characteristics: [
                                {
                                    name: "Цвет",
                                    value: "Белый"
                                },
                                {
                                    name: "Память",
                                    value: "256GB"
                                }
                            ] as Char[],
                            price: 38000,
                            quantity: 30
                        },
                        {
                            id: "3",
                            name: "128GB BLACK",
                            characteristics: [
                                {
                                    name: "Цвет",
                                    value: "Черный"
                                },
                                {
                                    name: "Память",
                                    value: "128GB"
                                }
                            ] as Char[],
                            price: 35000,
                            quantity: 25
                        },
                        {
                            id: "4",
                            name: "128GB WHITE",
                            characteristics: [
                                {
                                    name: "Цвет",
                                    value: "Белый"
                                },
                                {
                                    name: "Память",
                                    value: "128GB"
                                }
                            ] as Char[],
                            price: 32000,
                            quantity: 35
                        }
                    ]

        const sku = product.skus.filter((sku : SkuType) => sku.id === params.sku_id)[0]

        return {
            product: product,
            sku: sku,
        };
    } catch (error) {
        console.error("Error loading new_sku:", error);
        throw error;
    }
};