const API_BASE_URL = '/api';

export const categoryService = {
    // Get all categories
    async getAllCategories() {
        try {
            const response = await fetch(`${API_BASE_URL}/categories`);
            if (!response.ok) {
                throw new Error('Failed to fetch categories');
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching categories:', error);
            throw error;
        }
    },

    // Get categories for dropdown (simplified format)
    async getCategoriesForDropdown() {
        try {
            const response = await fetch(`${API_BASE_URL}/categories/dropdown`);
            if (!response.ok) {
                throw new Error('Failed to fetch categories for dropdown');
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching categories for dropdown:', error);
            throw error;
        }
    },

    // Get a single category
    async getCategory(id) {
        try {
            const response = await fetch(`${API_BASE_URL}/categories/${id}`);
            if (!response.ok) {
                throw new Error('Failed to fetch category');
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching category:', error);
            throw error;
        }
    },

    // Create a new category
    async createCategory(categoryData) {
        try {
            const response = await fetch(`${API_BASE_URL}/categories`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(categoryData),
            });
            if (!response.ok) {
                throw new Error('Failed to create category');
            }
            return await response.json();
        } catch (error) {
            console.error('Error creating category:', error);
            throw error;
        }
    },

    // Update a category
    async updateCategory(id, categoryData) {
        try {
            const response = await fetch(`${API_BASE_URL}/categories/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(categoryData),
            });
            if (!response.ok) {
                throw new Error('Failed to update category');
            }
            return await response.json();
        } catch (error) {
            console.error('Error updating category:', error);
            throw error;
        }
    },

    // Delete a category
    async deleteCategory(id) {
        try {
            const response = await fetch(`${API_BASE_URL}/categories/${id}`, {
                method: 'DELETE',
            });
            if (!response.ok) {
                throw new Error('Failed to delete category');
            }
            return await response.json();
        } catch (error) {
            console.error('Error deleting category:', error);
            throw error;
        }
    },

    // Add subcategory to a category
    async addSubCategory(categoryId, subCategoryData) {
        try {
            const response = await fetch(`${API_BASE_URL}/categories/${categoryId}/subcategories`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(subCategoryData),
            });
            if (!response.ok) {
                throw new Error('Failed to add subcategory');
            }
            return await response.json();
        } catch (error) {
            console.error('Error adding subcategory:', error);
            throw error;
        }
    },

    // Update subcategory
    async updateSubCategory(categoryId, subCategoryId, subCategoryData) {
        try {
            const response = await fetch(`${API_BASE_URL}/categories/${categoryId}/subcategories/${subCategoryId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(subCategoryData),
            });
            if (!response.ok) {
                throw new Error('Failed to update subcategory');
            }
            return await response.json();
        } catch (error) {
            console.error('Error updating subcategory:', error);
            throw error;
        }
    },

    // Delete subcategory
    async deleteSubCategory(categoryId, subCategoryId) {
        try {
            const response = await fetch(`${API_BASE_URL}/categories/${categoryId}/subcategories/${subCategoryId}`, {
                method: 'DELETE',
            });
            if (!response.ok) {
                throw new Error('Failed to delete subcategory');
            }
            return await response.json();
        } catch (error) {
            console.error('Error deleting subcategory:', error);
            throw error;
        }
    },

    // Initialize default categories
    async initializeDefaultCategories() {
        try {
            const response = await fetch(`${API_BASE_URL}/categories/initialize`, {
                method: 'POST',
            });
            if (!response.ok) {
                throw new Error('Failed to initialize default categories');
            }
            return await response.json();
        } catch (error) {
            console.error('Error initializing default categories:', error);
            throw error;
        }
    }
}; 