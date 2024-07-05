import { Routes } from '@angular/router';
import { SnippetsListComponent } from './documents/snippets-list.component';
import { DocumentDetailComponent } from './documents/document-detail.component';
import { CategoriesListComponent } from './documents/categories-list.component';

export const routes: Routes = [
	{ path: 'start', component: CategoriesListComponent },
	{ path: 'category/:id', component: SnippetsListComponent },
  	{ path: 'document/:id', component: DocumentDetailComponent },
	{ path: '', redirectTo: 'start', pathMatch: 'full' },
    { path: '**', redirectTo: 'start', pathMatch: 'full' }
];
