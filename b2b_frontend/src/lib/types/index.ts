export type ProductType = {
    id: string;
    title: string;
    description: string;
    category: Category;
    status: "active" | "blocked" | "inspection"
    characteristics: Char[];
    images: Image[];
    skus: SkuType[];
}

export type SkuType = {
    id: string;
    name: string;
    price: number;
    active_quantity: number;
    characteristics: Char[];
}

export type Char = {
    name: string;
    value: string;
}

export type Category = {
    id: string;
    value: string;
}

export type Image = {
    id: string;
    url: string;
    order: number;
}

export type InvoiceItem = {
    product: ProductType;
    sku: SkuType;
    quantity: number;
}

export type InvoiceType = {
    id: string;
    items: InvoiceItem[];
    date: Date;
}
