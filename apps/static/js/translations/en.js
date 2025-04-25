const translations = {
    en: {
        label: 'Label',
        file: 'File',
        required: '* Required',
        addRow: 'Add Another File',
        deleteSelect: 'Select to Delete Files',
        save: 'Save',
        close: 'Close',
        selectFolder: 'Please select the destination folder',
        selectFolderPlaceholder: 'Select a folder'
    },
    fr: {
        label: 'Étiquette',
        file: 'Fichier',
        required: '* Obligatoire',
        addRow: 'Ajouter un autre fichier',
        deleteSelect: 'Sélectionner pour supprimer des fichiers',
        save: 'Enregistrer',
        close: 'Fermer',
        selectFolder: 'Veuillez sélectionner le répertoire de destination',
        selectFolderPlaceholder: 'Sélectionner un dossier'
    }
};

function getUserLanguage() {
    return navigator.language.startsWith('fr') ? 'fr' : 'en';
}
