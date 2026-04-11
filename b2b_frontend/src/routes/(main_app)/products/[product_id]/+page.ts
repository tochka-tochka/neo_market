import type { PageLoad } from "../$types";
import { API_URL } from "$lib";
import type { ProductType, Char, Image } from "$lib/types";

export const load : PageLoad = async ({ params }) => {
    try {
        const res = await fetch(`${API_URL}/products/${params.product_id}/`,{
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("token")}`
            }
        }).then(res => res.json());
        const product : ProductType = res.product;
        console.log(product)
        if (!product.skus) {
            // product.skus = []
        }
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
        product.images = product.images.sort((a, b) => (a.order > b.order ? 1 : -1))
        return { "product" : product };
    } catch (error) {
        console.log(error);
    }
}