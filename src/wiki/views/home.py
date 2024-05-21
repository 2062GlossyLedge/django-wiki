from django.views.generic import TemplateView

from django.shortcuts import redirect, render
from openai import OpenAI


class Homepage(TemplateView):
    template_name = "wiki/homepage.html"
    client = OpenAI()


    def get_completion(prompt):
        print(prompt)
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            max_tokens=3000,
            temperature=0.4,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": 'You are a helpful assistant designed to output JSON. Always make one key name the key "response" and for the rest, make it the value to the key "response"  ',
                },
                {"role": "user", "content": prompt},
            ],
        )

        response = completion.choices[0].message.content
        print(response)
        return response


