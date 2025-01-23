import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { PersonService } from '../person.service';
import { Person } from '../person.model';

@Component({
  selector: 'app-person-form',
  templateUrl: './person-form.component.html',
  styleUrls: ['./person-form.component.css'],
})
export class PersonFormComponent implements OnInit {
  person: Person = new Person(0, '', 0, '');
  isEditMode: boolean = false;

  constructor(
    private personService: PersonService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Check if we're editing an existing person
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.isEditMode = true;
      this.getPerson(+id);
    }
  }

  // Fetch an existing person for editing
  getPerson(id: number): void {
    this.personService.getPerson(id).subscribe((data) => {
      this.person = data;
    });
  }

  // Save person data (add or update)
  savePerson(): void {
    if (this.isEditMode) {
      this.personService.updatePerson(this.person).subscribe(() => {
        this.router.navigate(['/people']); // Navigate back to the list
      });
    } else {
      this.personService.addPerson(this.person).subscribe(() => {
        this.router.navigate(['/people']); // Navigate back to the list
      });
    }
  }
}
