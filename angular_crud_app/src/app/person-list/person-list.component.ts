import { Component, OnInit } from '@angular/core';
import { PersonService } from '../person.service';
import { Person } from '../person.model';

@Component({
  selector: 'app-person-list',
  templateUrl: './person-list.component.html',
  styleUrls: ['./person-list.component.css']
})
export class PersonListComponent implements OnInit {
  people: Person[] = [];

  constructor(private personService: PersonService) {}

  ngOnInit(): void {
    this.getPeople();
  }

  getPeople(): void {
    this.personService.getPeople().subscribe((data) => {
      this.people = data;
    });
  }

  deletePerson(id: number): void {
    this.personService.deletePerson(id).subscribe(() => {
      this.getPeople(); // Refresh the list
    });
  }
}
