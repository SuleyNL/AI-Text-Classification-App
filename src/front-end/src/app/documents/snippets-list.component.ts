import { Component, OnDestroy, OnInit } from '@angular/core';
import { DocumentService } from './document.service';
import { ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import snippets from '../../api/documents/snippets2.json';
import { SafeHtmlPipe } from '../shared/pipes/safeHtml.pipe'

@Component({
  selector: 'app-snippets-list',
  standalone: true,
  imports: [CommonModule, RouterModule, SafeHtmlPipe],
  templateUrl: './snippets-list.component.html',
  styleUrl: './snippets-list.component.scss'
})
export class SnippetsListComponent implements OnInit, OnDestroy {
  sub!: Subscription;

  constructor(private documentService: DocumentService,
              private route: ActivatedRoute) {}

  snippets: any = [];

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));

    this.sub = this.documentService.getSnippets(id).subscribe({
      next: snippets => {
				this.snippets = snippets;
        console.log(snippets);
        
			},
			error: err => console.log(err)
    })
    // from json
    if (this.snippets.length === 0) {
      this.snippets = snippets;
    }
  }

  ngOnDestroy(): void {
		this.sub.unsubscribe();
	}
}
