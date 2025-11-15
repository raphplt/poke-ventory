<script setup lang="ts">
interface FileItem {
	file: File;
}

const files = ref<File[]>([]);

const handleUpdate = (fileItems: FileItem[]) => {
	files.value = fileItems.map((item) => item.file);
	// ici tu peux direct envoyer vers ton API, etc.
};
</script>

<template>
	<div>
		<h1>Import de cartes</h1>

		<div v-if="files">
			<h2 class="mt-4">Fichiers sélectionnés :</h2>
			<ul class="list-disc list-inside">
				<li v-for="(file, index) in files" :key="index">
					{{ file.name }} ({{ (file.size / 1024).toFixed(2) }} KB)
				</li>
			</ul>
		</div>

		<ClientOnly>
			<FilePond
				name="image"
				class="w-1/2 mx-auto mt-4"
				:allow-multiple="true"
				accepted-file-types="image/*"
				label-idle="Glisse-dépose une image ou <span class='filepond--label-action'>Parcourir</span>"
				@updatefiles="handleUpdate"
			/>
		</ClientOnly>
	</div>
</template>
