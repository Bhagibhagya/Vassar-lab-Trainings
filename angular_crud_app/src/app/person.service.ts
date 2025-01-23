import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Person } from './person.model';

@Injectable({
  providedIn: 'root'
})
export class PersonService {
  private apiUrl = 'http://127.0.0.1:8000/api/people/'; // Django API endpoint

  constructor(private http: HttpClient) {}

  // Get all people
  getPeople(): Observable<Person[]> {
    return this.http.get<Person[]>(this.apiUrl);
  }

  // Get a person by ID
  getPerson(id: number): Observable<Person> {
    return this.http.get<Person>(`${this.apiUrl}${id}/`);
  }

  // Add a new person
  addPerson(person: Person): Observable<Person> {
    return this.http.post<Person>(this.apiUrl, person);
  }

  // Update a person
  updatePerson(person: Person): Observable<Person> {
    return this.http.put<Person>(`${this.apiUrl}${person.id}/`, person);
  }

  // Delete a person
  deletePerson(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}${id}/`);
  }
}
