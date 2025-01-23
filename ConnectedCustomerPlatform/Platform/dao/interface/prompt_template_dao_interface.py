from abc import ABC, abstractmethod

class IPromptTemplateDao(ABC):

    @abstractmethod
    def save_prompt_template(self, prompt_template):
        """
            Saves the provided prompt_template object in the database.

            :param prompt_template: An instance of PromptTemplate to be saved.
            :return: The saved instance of PromptTemplate.
        """

    @abstractmethod
    def update_prompt_template(self, prompt_template_uuid, prompt_template_name, prompt_category_uuid, prompt_template_description, prompt_template_details_dict, user_uuid):
        """
            Updates prompt_template by id.
            :param prompt_template_uuid : prompt_template uuid need to be update
            :param prompt_template_name : updated name
            :param prompt_category_uuid : updated category
            :param prompt_template_description : updated description
            :param prompt_template_details_dict : updated template_details_json
            :param user_uuid : user uuid who updating the prompt_template
            :return: updated instance of prompt_template
        """

    @abstractmethod
    def get_prompt_templates(self):
        """
            Fetches all prompt_templates.
            :return: Instances of prompt_templates
        """

    @abstractmethod
    def delete_prompt_template(self, prompt_template_uuid, user_uuid):
        """
            Deletes prompt_category : marks is_deleted as true .
            :param prompt_template_uuid : prompt_template uuid to be deleted
            :param user_uuid : user uuid who deleting the prompt_template
            :return: no of rows effected
        """

    @abstractmethod
    def get_prompt_categories(self):
        """
            Fetches all prompt_categories .
            :return: None
        """