<script setup lang="ts">
import type { Card, CardFilters, Series, Set } from "~/types/api";

interface Props {
	importType: "cards" | "products";
}

const props = defineProps<Props>();

const { getCards, getSeries, getSets } = useCards();
const { addUserCardsBatch } = useUserCards();

// État de recherche
const searchQuery = ref("");
const isSearching = ref(false);
const searchResults = ref<Card[]>([]);
const totalResults = ref(0);
const currentPage = ref(1);
const pageSize = ref(20);

// Filtres
const filters = ref<CardFilters>({
	skip: 0,
	limit: pageSize.value,
});
const showFilters = ref(false);

// Options pour les filtres
const series = ref<Series[]>([]);
const sets = ref<Set[]>([]);
const selectedSeriesId = ref<string | null>(null);
const selectedSetId = ref<string | null>(null);
const selectedRarity = ref<string | null>(null);
const selectedCategory = ref<string | null>(null);
const selectedType = ref<string | null>(null);
const selectedStage = ref<string | null>(null);

// États UI
const errorMessage = ref<string | null>(null);
const successMessage = ref<string | null>(null);
const selectedCards = ref<Set<string>>(new Set());
const isAdding = ref(false);

// Raretés communes
const rarities = [
	"Common",
	"Uncommon",
	"Rare",
	"Ultra Rare",
	"Secret Rare",
	"Rare Holo",
	"Rare Holo EX",
	"Rare Holo GX",
	"Rare Holo V",
	"Rare Holo VMAX",
	"Rare Holo VSTAR",
];

// Catégories
const categories = ["Pokemon", "Trainer", "Energy"];

// Stages
const stages = ["Basic", "Stage1", "Stage2"];

// Types Pokémon
const pokemonTypes = [
	"Grass",
	"Fire",
	"Water",
	"Lightning",
	"Psychic",
	"Fighting",
	"Darkness",
	"Metal",
	"Fairy",
	"Dragon",
	"Colorless",
];

// Charger les séries et sets au montage
onMounted(async () => {
	try {
		const seriesData = await getSeries();
		series.value = seriesData.data.value || [];
	} catch (error) {
		console.error("Erreur lors du chargement des séries:", error);
	}
});

// Charger les sets quand une série est sélectionnée
watch(selectedSeriesId, async (newSeriesId) => {
	if (newSeriesId) {
		try {
			const setsData = await getSets(newSeriesId);
			sets.value = setsData.data.value || [];
			selectedSetId.value = null;
		} catch (error) {
			console.error("Erreur lors du chargement des sets:", error);
		}
	} else {
		sets.value = [];
		selectedSetId.value = null;
	}
});

// Effectuer la recherche
const performSearch = async (page = 1) => {
	if (!searchQuery.value.trim() && !hasActiveFilters()) {
		errorMessage.value = "Saisis au moins un mot-clé ou utilise des filtres pour lancer la recherche.";
		return;
	}

	isSearching.value = true;
	errorMessage.value = null;
	successMessage.value = null;
	currentPage.value = page;

	// Construire les filtres
	const searchFilters: CardFilters = {
		skip: (page - 1) * pageSize.value,
		limit: pageSize.value,
	};

	if (searchQuery.value.trim()) {
		searchFilters.name = searchQuery.value.trim();
	}
	if (selectedSetId.value) {
		searchFilters.set_id = selectedSetId.value;
	}
	if (selectedSeriesId.value) {
		searchFilters.series_id = selectedSeriesId.value;
	}
	if (selectedRarity.value) {
		searchFilters.rarity = selectedRarity.value;
	}
	if (selectedCategory.value) {
		searchFilters.category = selectedCategory.value;
	}
	if (selectedType.value) {
		searchFilters.type = selectedType.value;
	}
	if (selectedStage.value) {
		searchFilters.stage = selectedStage.value;
	}

	try {
		const response = await getCards(searchFilters);
		const data = response.data.value;
		if (data) {
			searchResults.value = data.items || [];
			totalResults.value = data.total || 0;
		} else {
			searchResults.value = [];
			totalResults.value = 0;
		}
	} catch (error: unknown) {
		errorMessage.value =
			error instanceof Error
				? error.message
				: "Une erreur est survenue lors de la recherche.";
		searchResults.value = [];
		totalResults.value = 0;
	} finally {
		isSearching.value = false;
	}
};

// Vérifier si des filtres sont actifs
const hasActiveFilters = () => {
	return !!(
		selectedSetId.value ||
		selectedSeriesId.value ||
		selectedRarity.value ||
		selectedCategory.value ||
		selectedType.value ||
		selectedStage.value
	);
};

// Réinitialiser les filtres
const resetFilters = () => {
	selectedSeriesId.value = null;
	selectedSetId.value = null;
	selectedRarity.value = null;
	selectedCategory.value = null;
	selectedType.value = null;
	selectedStage.value = null;
};

// Toggle sélection d'une carte
const toggleCardSelection = (cardId: string) => {
	if (selectedCards.value.has(cardId)) {
		selectedCards.value.delete(cardId);
	} else {
		selectedCards.value.add(cardId);
	}
};

// Ajouter les cartes sélectionnées
const addSelectedCards = async () => {
	if (selectedCards.value.size === 0) {
		errorMessage.value = "Sélectionne au moins une carte à ajouter.";
		return;
	}

	isAdding.value = true;
	errorMessage.value = null;
	successMessage.value = null;

	try {
		const cardsToAdd = Array.from(selectedCards.value).map((cardId) => ({
			card_id: cardId,
			quantity: 1,
		}));

		const response = await addUserCardsBatch(cardsToAdd);
		const itemType = props.importType === "cards" ? "carte(s)" : "produit(s)";
		const destination =
			props.importType === "cards" ? "collection" : "inventaire";

		if (response.created > 0 || response.updated > 0) {
			successMessage.value = `${response.created + response.updated} ${itemType} ajouté(s) à ta ${destination} !`;
			selectedCards.value.clear();
		} else {
			errorMessage.value = "Aucune carte n'a pu être ajoutée.";
		}
	} catch (error: unknown) {
		errorMessage.value =
			error instanceof Error ? error.message : "Une erreur est survenue.";
	} finally {
		isAdding.value = false;
	}
};

// Réinitialiser la recherche
const resetSearch = () => {
	searchQuery.value = "";
	searchResults.value = [];
	selectedCards.value.clear();
	errorMessage.value = null;
	successMessage.value = null;
	currentPage.value = 1;
	totalResults.value = 0;
	resetFilters();
};

// Calculer le nombre de pages
const totalPages = computed(() => {
	return Math.ceil(totalResults.value / pageSize.value);
});

// Pagination
const goToPage = (page: number) => {
	if (page >= 1 && page <= totalPages.value) {
		performSearch(page);
	}
};
</script>

<template>
	<div class="space-y-6">
		<div>
			<h2 class="text-xl font-semibold text-gray-900 mb-1">
				Import par recherche
			</h2>
			<p class="text-sm text-gray-600">
				{{
					props.importType === "cards"
						? "Recherche des cartes dans notre base de données et ajoute-les à ta collection."
						: "Recherche des produits scellés dans notre base de données et ajoute-les à ton inventaire."
				}}
			</p>
		</div>

		<!-- Barre de recherche -->
		<div class="rounded-lg border border-gray-200 bg-gray-50 p-4">
			<div class="flex gap-2 mb-3">
				<input
					v-model="searchQuery"
					type="text"
					:placeholder="
						props.importType === 'cards'
							? 'Ex: Pikachu, Dracaufeu, Base Set...'
							: 'Ex: Booster Écarlate et Violet, Display Paradoxe...'
					"
					class="flex-1 px-4 py-2 text-sm border border-gray-300 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
					@keyup.enter="performSearch(1)"
				/>
				<button
					class="px-5 py-2 text-sm font-medium text-white bg-blue-600 rounded-md disabled:opacity-50 hover:bg-blue-700 transition-colors shrink-0"
					:disabled="isSearching || (!searchQuery.trim() && !hasActiveFilters())"
					@click="performSearch(1)"
				>
					{{ isSearching ? "Recherche..." : "Rechercher" }}
				</button>
				<button
					v-if="showFilters || hasActiveFilters()"
					class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
					@click="showFilters = !showFilters"
				>
					{{ showFilters ? "Masquer" : "Afficher" }} les filtres
				</button>
			</div>

			<!-- Filtres avancés -->
			<div v-if="showFilters || hasActiveFilters()" class="mt-4 pt-4 border-t border-gray-200">
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
					<!-- Série -->
					<div>
						<label class="block text-xs font-medium text-gray-700 mb-1">
							Série
						</label>
						<select
							v-model="selectedSeriesId"
							class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
						>
							<option :value="null">Toutes les séries</option>
							<option
								v-for="s in series"
								:key="s.id"
								:value="s.id"
							>
								{{ s.name }}
							</option>
						</select>
					</div>

					<!-- Set -->
					<div>
						<label class="block text-xs font-medium text-gray-700 mb-1">
							Set
						</label>
						<select
							v-model="selectedSetId"
							class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
							:disabled="!selectedSeriesId"
						>
							<option :value="null">Tous les sets</option>
							<option
								v-for="set in sets"
								:key="set.id"
								:value="set.id"
							>
								{{ set.name }}
							</option>
						</select>
					</div>

					<!-- Rareté -->
					<div>
						<label class="block text-xs font-medium text-gray-700 mb-1">
							Rareté
						</label>
						<select
							v-model="selectedRarity"
							class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
						>
							<option :value="null">Toutes les raretés</option>
							<option
								v-for="rarity in rarities"
								:key="rarity"
								:value="rarity"
							>
								{{ rarity }}
							</option>
						</select>
					</div>

					<!-- Catégorie -->
					<div>
						<label class="block text-xs font-medium text-gray-700 mb-1">
							Catégorie
						</label>
						<select
							v-model="selectedCategory"
							class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
						>
							<option :value="null">Toutes les catégories</option>
							<option
								v-for="cat in categories"
								:key="cat"
								:value="cat"
							>
								{{ cat }}
							</option>
						</select>
					</div>

					<!-- Type -->
					<div>
						<label class="block text-xs font-medium text-gray-700 mb-1">
							Type
						</label>
						<select
							v-model="selectedType"
							class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
						>
							<option :value="null">Tous les types</option>
							<option
								v-for="type in pokemonTypes"
								:key="type"
								:value="type"
							>
								{{ type }}
							</option>
						</select>
					</div>

					<!-- Stage -->
					<div>
						<label class="block text-xs font-medium text-gray-700 mb-1">
							Stage
						</label>
						<select
							v-model="selectedStage"
							class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
						>
							<option :value="null">Tous les stages</option>
							<option
								v-for="stage in stages"
								:key="stage"
								:value="stage"
							>
								{{ stage }}
							</option>
						</select>
					</div>
				</div>

				<div v-if="hasActiveFilters()" class="mt-4 flex justify-end">
					<button
						class="px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
						@click="resetFilters"
					>
						Réinitialiser les filtres
					</button>
				</div>
			</div>
		</div>

		<!-- Messages d'erreur/succès -->
		<div
			v-if="errorMessage"
			class="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700"
		>
			{{ errorMessage }}
		</div>

		<div
			v-if="successMessage"
			class="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700"
		>
			{{ successMessage }}
		</div>

		<!-- Résultats -->
		<div v-if="searchResults.length > 0" class="space-y-4">
			<div class="flex items-center justify-between">
				<div>
					<h3 class="text-lg font-semibold text-gray-900">
						Résultats ({{ totalResults }})
					</h3>
					<p v-if="selectedCards.size > 0" class="text-sm text-gray-600 mt-1">
						{{ selectedCards.size }} carte(s) sélectionnée(s)
					</p>
				</div>
				<button
					v-if="selectedCards.size > 0"
					class="px-4 py-2 text-sm font-medium text-white bg-emerald-600 rounded-md hover:bg-emerald-700 transition-colors disabled:opacity-50"
					:disabled="isAdding"
					@click="addSelectedCards"
				>
					{{ isAdding ? "Ajout..." : `Ajouter ${selectedCards.size} carte(s)` }}
				</button>
			</div>

			<!-- Grille de cartes -->
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
				<div
					v-for="card in searchResults"
					:key="card.id"
					class="rounded-lg border p-4 cursor-pointer transition-all hover:shadow-md"
					:class="
						selectedCards.has(card.id)
							? 'border-blue-500 bg-blue-50 ring-2 ring-blue-500'
							: 'border-gray-200 bg-white hover:border-gray-300'
					"
					@click="toggleCardSelection(card.id)"
				>
					<div class="flex items-start gap-3">
						<input
							type="checkbox"
							:checked="selectedCards.has(card.id)"
							class="mt-1 text-blue-600 focus:ring-blue-500"
							@click.stop="toggleCardSelection(card.id)"
						/>
						<div class="flex-1 min-w-0">
							<div v-if="card.image" class="mb-2">
								<img
									:src="card.image"
									:alt="card.name"
									class="w-full h-32 object-contain rounded"
								/>
							</div>
							<p class="font-semibold text-sm text-gray-900 truncate">
								{{ card.name }}
							</p>
							<p class="text-xs text-gray-500 mt-1">
								#{{ card.local_id }}
							</p>
							<div v-if="card.rarity" class="mt-1">
								<span
									class="inline-block px-2 py-0.5 text-xs font-medium rounded bg-gray-100 text-gray-700"
								>
									{{ card.rarity }}
								</span>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Pagination -->
			<div v-if="totalPages > 1" class="flex items-center justify-center gap-2 pt-4">
				<button
					class="px-3 py-2 text-sm border border-gray-300 rounded-md bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
					:disabled="currentPage === 1"
					@click="goToPage(currentPage - 1)"
				>
					Précédent
				</button>
				<span class="px-4 py-2 text-sm text-gray-700">
					Page {{ currentPage }} sur {{ totalPages }}
				</span>
				<button
					class="px-3 py-2 text-sm border border-gray-300 rounded-md bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
					:disabled="currentPage === totalPages"
					@click="goToPage(currentPage + 1)"
				>
					Suivant
				</button>
			</div>

			<div class="pt-4 border-t border-gray-200">
				<button
					class="text-sm text-gray-500 underline hover:text-gray-700"
					@click="resetSearch"
				>
					Nouvelle recherche
				</button>
			</div>
		</div>

		<!-- État vide -->
		<div
			v-else-if="!isSearching && searchQuery.trim() === '' && !hasActiveFilters()"
			class="rounded-lg border border-gray-200 bg-gray-50 p-8 text-center"
		>
			<p class="text-gray-600">
				Utilise la barre de recherche ou les filtres pour trouver des cartes.
			</p>
		</div>
	</div>
</template>
