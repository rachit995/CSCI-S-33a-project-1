from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
import markdown2
import random as random_from_stdlib


from . import util


# Create a form for adding and editing entries
class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(widget=forms.Textarea, label="Content")


def index(request):
    return render(request, "encyclopedia/index.html", {"entries": util.list_entries()})


def entry(request, title):
    # If the entry exists, display it
    try:
        # Convert the markdown to HTML
        entry = markdown2.markdown(util.get_entry(title))
    except TypeError:
        # If the entry doesn't exist, display an error
        entry = "Page not found"
    return render(
        request,
        "encyclopedia/entry.html",
        {"entry": entry, "title": title},
    )


def search(request):
    # Get the query from the form
    query = request.GET.get("q")
    # If the query is an exact match for an entry, redirect to that entry
    if util.get_entry(query):
        # Redirect to the entry
        return HttpResponseRedirect(
            reverse(
                "entry",
                kwargs={"title": query},
            )
        )
    else:
        # If the query is not an exact match for an entry, display a list of entries that match the query
        # Get a list of all entries
        entries = util.list_entries()
        results = []
        # Check if the query is a substring of any of the entries
        for entry in entries:
            if query.lower() in entry.lower():
                results.append(entry)
        return render(request, "encyclopedia/search.html", {"results": results})


def add(request):
    # If the form has been submitted, validate it and save the entry
    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = NewEntryForm(request.POST)
        # Check whether the form is valid
        if form.is_valid():
            # Process the data in form.cleaned_data as required
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            # Check if the entry already exists
            if util.get_entry(title):
                # If the entry already exists, display an error
                return render(
                    request,
                    "encyclopedia/add.html",
                    {
                        "form": form,
                        "error": "Entry already exists",
                    },
                )
            else:
                # If the entry doesn't exist, save it and redirect to the entry
                util.save_entry(title, content)
                return HttpResponseRedirect(
                    reverse(
                        "entry",
                        kwargs={"title": title},
                    )
                )
        else:
            # If the form is invalid, display an error
            return render(
                request,
                "encyclopedia/add.html",
                {
                    "form": form,
                    "error": "Invalid form",
                },
            )
    else:
        # If the form hasn't been submitted, display a blank form
        return render(
            request,
            "encyclopedia/add.html",
            {
                "form": NewEntryForm(),
            },
        )


def edit(request, title):
    # If the form has been submitted, validate it and save the entry
    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = NewEntryForm(request.POST)
        # Check whether the form is valid
        if form.is_valid():
            # Process the data in form.cleaned_data as required
            content = form.cleaned_data["content"]
            # Save the entry and redirect to the entry
            util.save_entry(title, content)
            # Redirect to the entry
            return HttpResponseRedirect(
                reverse(
                    "entry",
                    kwargs={"title": title},
                )
            )
        else:
            # If the form is invalid, display an error
            return render(
                request,
                "encyclopedia/edit.html",
                {
                    "form": form,
                    "title": title,
                    "error": "Invalid form",
                },
            )
    else:
        # If the form hasn't been submitted, display a form with the entry's current content
        content = util.get_entry(title)
        # Create a form instance and populate it with data from the request
        form = NewEntryForm({"title": title, "content": content})
        # Make the title read-only
        form.fields["title"].widget.attrs["readonly"] = True
        # Display the form
        return render(
            request,
            "encyclopedia/edit.html",
            {
                "form": form,
                "title": title,
            },
        )


def random(request):
    # Get a list of all entries
    entries = util.list_entries()
    # Redirect to a random entry
    return HttpResponseRedirect(
        reverse(
            "entry",
            kwargs={"title": random_from_stdlib.choice(entries)},
        )
    )
