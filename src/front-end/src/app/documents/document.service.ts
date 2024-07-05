import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, catchError, tap, throwError, map } from "rxjs";


@Injectable({
  providedIn: 'root'
})
export class DocumentService {
  private categoriesUrl = 'http://127.0.0.1:8001/persons/1/categories';
  private snippetsUrl = 'http://127.0.0.1:8001/persons/1/';
  private documentUrl = 'http://127.0.0.1:8001/docs/';

  constructor(private http: HttpClient) { }

  // GET request to fetch Categories linked to person id
  // Query variable: person id
  getCategories(): Observable<any> {
		return this.http.get(this.categoriesUrl)
		.pipe(
			tap(data => console.log('All', JSON.stringify(data))),
			catchError(this.handleError)
		);
	}

	// GET request to fetch all snippets linked to person id and category id
	// Query variable: person id, category id
	getSnippets(cat_id: Number): Observable<any> {
		return this.http.get(`${this.snippetsUrl}${cat_id}`)
    .pipe(
			tap(data => console.log('All', JSON.stringify(data))),
			catchError(this.handleError)
		);
	}

  getDocument(doc_id: Number): Observable<any> {
		return this.http.get(`${this.documentUrl}${doc_id}`)
    .pipe(
			tap(data => console.log('All', JSON.stringify(data))),
			catchError(this.handleError)
		);
	}

  // getDocument(id: number): Observable<any | undefined> {
	// 	return this.getDocuments()
	// 	  .pipe(
  //     // tap(data => console.log('All', JSON.stringify(data))),
	// 		map((documents: any) => documents.find((item: { id: number; }) => item.id === id))
	// 	  );
	//   }

  private handleError(err: HttpErrorResponse) {
		let errorMessage = '';
		if (err.error instanceof ErrorEvent) {
			errorMessage = `An error occurred: ${err.error.message}`;
		} else {
			errorMessage = `Server returned code: ${err.status}, error message is: ${err.message}`
		}
		console.log(errorMessage);
		return throwError(()=>errorMessage)
	}
}
