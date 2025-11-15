/**
 * Types pour les entités de l'API
 */

export interface Card {
	id: string;
	local_id: string;
	name: string;
	image: string | null;
	hp: number | null;
	types: string[] | null;
	evolves_from: string | null;
	stage: string | null;
	rarity: string | null;
	category: string | null;
	illustrator: string | null;
	set_id: string;
	created_at: string;
	updated_at: string | null;
}

export interface Set {
	id: string;
	tcgdex_id: string;
	name: string;
	logo: string | null;
	card_count: {
		total: number;
		official: number;
	};
	series_id: string;
	created_at: string;
	updated_at: string | null;
}

export interface Series {
	id: string;
	tcgdex_id: string;
	name: string;
	created_at: string;
	updated_at: string | null;
}

// Filtres
export interface CardFilters {
	set_id?: string;
	name?: string;
	rarity?: string;
	type?: string;
	skip?: number;
	limit?: number;
}

export interface SetFilters {
	series_id?: string;
	name?: string;
	skip?: number;
	limit?: number;
}
