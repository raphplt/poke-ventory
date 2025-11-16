import type { Card, CardFilters, CardsResponse, Series, Set } from "~/types/api";

/**
 * Composable pour gérer les cartes Pokémon
 */
export const useCards = () => {
	const api = useApi();

	/**
	 * Récupérer la liste des cartes avec filtres et pagination
	 */
	const getCards = (filters?: CardFilters) => {
		const params = new URLSearchParams();

		if (filters?.set_id) params.append("set_id", filters.set_id);
		if (filters?.series_id) params.append("series_id", filters.series_id);
		if (filters?.name) params.append("name", filters.name);
		if (filters?.rarity) params.append("rarity", filters.rarity);
		if (filters?.category) params.append("category", filters.category);
		if (filters?.type) params.append("type", filters.type);
		if (filters?.stage) params.append("stage", filters.stage);
		if (filters?.local_id) params.append("local_id", filters.local_id);
		if (filters?.skip !== undefined) params.append("skip", filters.skip.toString());
		if (filters?.limit !== undefined) params.append("limit", filters.limit.toString());

		const queryString = params.toString();
		const url = queryString ? `/cards/?${queryString}` : "/cards/";

		return api.get<CardsResponse>(url);
	};

	/**
	 * Récupérer toutes les séries
	 */
	const getSeries = () => {
		return api.get<Series[]>("/series/");
	};

	/**
	 * Récupérer tous les sets
	 */
	const getSets = (seriesId?: string) => {
		const params = new URLSearchParams();
		if (seriesId) params.append("series_id", seriesId);
		const queryString = params.toString();
		const url = queryString ? `/sets/?${queryString}` : "/sets/";
		return api.get<Set[]>(url);
	};

	/**
	 * Récupérer une carte par son ID
	 */
	const getCard = (cardId: string) => {
		return api.get<Card>(`/cards/${cardId}`);
	};

	/**
	 * Créer une carte (nécessite authentification)
	 */
	const createCard = async (card: Partial<Card>) => {
		return await api.post<Card>("/cards/", card);
	};

	/**
	 * Mettre à jour une carte (nécessite authentification)
	 */
	const updateCard = async (cardId: string, card: Partial<Card>) => {
		return await api.put<Card>(`/cards/${cardId}`, card);
	};

	/**
	 * Supprimer une carte (nécessite authentification)
	 */
	const deleteCard = async (cardId: string) => {
		return await api.delete(`/cards/${cardId}`);
	};

	return {
		getCards,
		getCard,
		createCard,
		updateCard,
		deleteCard,
		getSeries,
		getSets,
	};
};
