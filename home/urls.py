from django.urls import path

from .views import (
    BookListView, BookDetailView, BookCreateView, BookUpdateView, BookDeleteView,
    AuthorListView, AuthorDetailView, AuthorUpdateView, AuthorDeleteView, SeriesCreateView,
    TopicListView, TopicDeleteView, TopicDetailView, TopicCreateView, TopicUpdateView,
    TransactionListView, TransactionDetailView, TransactionDeleteView,
    PublisherListView, PublisherDetailView, PublisherCreateView, PublisherUpdateView, PublisherDeleteView, 
    SeriesListView, SeriesDeleteView, SeriesDetailView, SeriesUpdateView,
    CoverListView, CoverDetailView, CoverCreateView, CoverUpdateView, CoverDeleteView,
    CustomerListView, CustomerDetailView, CustomerUpdateView, CustomerDeleteView, BrowseBookListView
)
from . import views

urlpatterns = [
    path('admin/', views.administrator, name='admin'),
    path('legal/', views.legal, name='legal'),
    path('privacy/', views.privacy, name='privacy'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('', views.home, name='bookshelf-home'),

    # Books routes
    path('browse/', BrowseBookListView.as_view(), name='browse'),
    path('browseall/', BookListView.as_view(), name='browse-all'),
    path('browseall/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('browseall/create/', views.bookCreateView, name='book-create'),
    path('browseall/update/<int:pk>/', BookUpdateView.as_view(), name='book-update'),
    path('browseall/delete/<int:pk>/', BookDeleteView.as_view(), name='book-delete'),

    # Author routes
    path('authors/', AuthorListView.as_view(), name="authors"),
    path('authors/<int:pk>/',AuthorDetailView.as_view(), name='author-detail'),
    path('authors/create/', views.authorCreateView, name='author-create'),
    path('authors/update/<int:pk>/',AuthorUpdateView.as_view(), name='author-update'),
    path('authors/delete/<int:pk>/',AuthorDeleteView.as_view(), name='author-delete'),

    # Topic routes
    path('topics/', TopicListView.as_view(), name="topics"),
    path('topics/<int:pk>/', TopicDetailView.as_view(), name='topic-detail'),
    path('topics/create/', TopicCreateView.as_view(), name='topic-create'),
    path('topics/update/<int:pk>/', TopicUpdateView.as_view(), name='topic-update'),
    path('topics/delete/<int:pk>/', TopicDeleteView.as_view(), name='topic-delete'),

    # Transaction routes
    path('transactions/', TransactionListView.as_view(), name="transactions"),
    path('transactions/<int:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),
    path('transactions/create/', views.transactionCreateView, name='transaction-create'),
    path('transactions/update/<int:pk>/', views.transactionUpdateView, name='transaction-update'),
    path('transactions/delete/<int:pk>/', TransactionDeleteView.as_view(), name='transaction-delete'),

    # Internal API routes
    path('api/books/', views.getBookData, name="apiBooks"),
    path('api/transactions/', views.getTransactionData, name="apiTransactions"),
    path('api/books', views.getBookData, name="apiBooks"),
    path('api/transactions', views.getTransactionData, name="apiTransactions"),

    # Internal list queries
    path('api/authorInput/', views.authorInput, name="apiAuthorInput"),
    path('api/topicInput/', views.topicInput, name="apiTopicInput"),
    path('api/bookInput/', views.bookInput, name="apiBookInput"),
    path('api/customerInput/', views.customerInput, name="apiCustomerInput"),
    path('api/coverInput/', views.coverInput, name="apicoverInput"),
    path('api/conditionInput/', views.conditionInput, name="apiConditionInput"),
    path('api/publisherInput/', views.publisherInput, name="apiPublisherInput"),
    path('api/seriesInput/', views.seriesInput, name="apiSeriesInput"),

    # COGS Report
    path('dashboard/cogs/<int:year>/', views.cogsReport, name='cogs'),

    # Publisher routes
    path('publishers/', PublisherListView.as_view(), name="publishers"),
    path('publishers/<int:pk>/', PublisherDetailView.as_view(), name="publisher-detail"),
    path('publishers/create/', PublisherCreateView.as_view(), name='publisher-create'),
    path('publishers/update/<int:pk>/', PublisherUpdateView.as_view(), name='publisher-update'),
    path('publishers/delete/<int:pk>/', PublisherDeleteView.as_view(), name='publisher-delete'),

    # Series routes
    path('series/', SeriesListView.as_view(), name="series"),
    path('series/<int:pk>/', SeriesDetailView.as_view(), name="series-detail"),
    path('series/create/', SeriesCreateView.as_view(), name='series-create'),
    path('series/update/<int:pk>/', SeriesUpdateView.as_view(), name='series-update'),
    path('series/delete/<int:pk>/', SeriesDeleteView.as_view(), name='series-delete'),

    # Customers routes
    path('customers/', CustomerListView.as_view(), name="customers"),
    path('customers/<int:pk>/', CustomerDetailView.as_view(), name="customers-detail"),
    path('customers/create/', views.customersCreateView, name='customers-create'),
    path('customers/update/<int:pk>/', CustomerUpdateView.as_view(), name='customers-update'),
    path('customers/delete/<int:pk>/', CustomerDeleteView.as_view(), name='customers-delete'),

    # Cover Types routes
    path('covers/', CoverListView.as_view(), name="covers"),
    path('covers/<int:pk>/', CoverDetailView.as_view(), name="covers-detail"),
    path('covers/create/', CoverCreateView.as_view(), name='covers-create'),
    path('covers/update/<int:pk>/', CoverUpdateView.as_view(), name='covers-update'),
    path('covers/delete/<int:pk>/', CoverDeleteView.as_view(), name='covers-delete'),
]

# app/model_viewtype.html