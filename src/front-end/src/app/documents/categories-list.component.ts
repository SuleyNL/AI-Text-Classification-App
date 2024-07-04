import { Component, OnDestroy, OnInit } from '@angular/core';
import { DocumentService } from './document.service';
import { Subscription } from 'rxjs';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import categories from '../../api/documents/categories.json';

@Component({
  selector: 'app-categories-list',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './categories-list.component.html',
  styleUrl: './categories-list.component.scss'
})
export class CategoriesListComponent implements OnInit, OnDestroy {
  sub!: Subscription;

  constructor(private documentService: DocumentService) {}

  categories: any = [];

  ngOnInit(): void {
    // this.sub = this.documentService.getCategories().subscribe({
    //   next: categories => {
		// 		this.categories = categories;
    //     console.log(categories);
        
		// 	},
		// 	error: err => console.log(err)
    // })
    this.categories = categories;
  }

  ngOnDestroy(): void {
		// this.sub.unsubscribe();
	}
}
