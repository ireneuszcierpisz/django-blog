from django.shortcuts import render, get_object_or_404, reverse
from django.views import generic
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Post, Comment
from .forms import CommentForm

# Create your views here.
class PostList(generic.ListView):
    # model = Post
    queryset = Post.objects.filter(status=1)
    template_name = "blog/index.html"
    # template_name = "index.html"
    paginate_by = 6


def post_detail(request, slug):
    """
    Display an individual :model:`blog.Post`.

    **Context**

    ``post``
        An instance of :model:`blog.Post`.

    **Template:**

    :template:`blog/post_detail.html`
    """

    queryset = Post.objects.filter(status=1)
    post = get_object_or_404(queryset, slug=slug)
    comments = post.comments.all().order_by("-created_on")
    comment_count = post.comments.filter(approved=True).count()
    if request.method == "POST":
        print("Received a POST request")
        # create an instance of the CommentForm class
        # using the form data that was sent in the POST request.
        comment_form = CommentForm(data=request.POST)
        # the form data is the comment's text
        # as specified in forms.py, this will be stored in the body field.
        #  if the form has been filled out correctly:
        if comment_form.is_valid():
            # Calling the save method with commit=False 
            # returns an object that hasn't yet been saved to the database
            # so that we can modify it further.
            # We do this because we need to populate the post field
            # and author fieldd before we save.
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.post = post
            # The object will not be written to the database
            # until we call the save method again.
            comment.save()
            # Django's message framework is a way of providing notifications
            # function accepts a request, a message tag and message text.
            # When a message is added we display it using the code
            # added below the nav in base.html.
            messages.add_message(
                request, messages.SUCCESS,
                'Comment submitted and awaiting approval'
            )
    # create a blank instance of the CommentForm class.
    # this line resets the content of the form to blank
    # so that a user can write a second comment if they wish.
    comment_form = CommentForm()
    print("About to render template")
    return render(
        request,
        "blog/post_detail.html",
        {
            "post": post,
            "comments": comments,
            "comment_count": comment_count,
            "comment_form": comment_form,
         },
    )


def comment_edit(request, slug, comment_id):
    """
    view to edit comments
    """
    if request.method == "POST":

        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comment = get_object_or_404(Comment, pk=comment_id)
        comment_form = CommentForm(data=request.POST, instance=comment)

        if comment_form.is_valid() and comment.author == request.user:
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.approved = False
            comment.save()
            messages.add_message(request, messages.SUCCESS, 'Comment Updated!')
        else:
            messages.add_message(request, messages.ERROR,
                                 'Error updating comment!')

    return HttpResponseRedirect(reverse('post_detail', args=[slug]))
