from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import admin, messages
from django.db.models import Q
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from .models import *
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db import connection
from django import forms
import json
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


# Plain HTML views
def home(req):
    return render(req, 'home/home.html')
def legal(req):
    return render(req, 'home/legal-statement.html')
def privacy(req):
    return render(req, 'home/privacy-statement.html')
@login_required
def administrator(req):
    return render(req, admin.site.urls)
def about(req):
    return render(req, 'home/about.html')
@login_required
def dashboard(req):
    return render(req, 'home/dashboard.html')


# View for the COGS report
@login_required
def cogsReport(request, year):
    old_year = str(year - 1)
    new_year = str(year)
    beginning = '''
        SELECT 
        (SELECT SUM("InOut"*"Price"*"Qty") AS 'All Inventory' 
        FROM home_transactions 
        WHERE ("Type" = 'Trade' OR "Type" = 'Purchase by Store') AND ("DateOfSale" BETWEEN '1992-12-31' AND (%s) || '-12-31')) + 
        (SELECT SUM("InOut"*("Price"/2)*"Qty") 'All Sales' 
        FROM home_transactions 
        WHERE "Type" = 'Sales' AND ("DateOfSale" BETWEEN '1992-12-31' AND (%s) || '-12-31')) 'Beginning Inventory'
    '''
    with connection.cursor() as cursor:
        cursor.execute(beginning % (old_year, old_year))
        beg_inv = cursor.fetchall()
    beg_dols = []
    for item in beg_inv:
        beg_dols.append(item[0])
    purchases = '''
        SELECT SUM("InOut"*"Price"*"Qty") 'Purchases'
        FROM home_transactions
        WHERE "DateOfSale" BETWEEN (%s) || '-01-01' AND (%s) || '-12-31' AND ("Type" = 'Purchase by Store' OR "Type" = 'Trade')
    '''
    with connection.cursor() as cursor:
        cursor.execute(purchases % (new_year, new_year))
        purch = cursor.fetchall()
    purchs = []
    for books in purch:
        purchs.append(books[0])
    ending = '''
        SELECT 
        (SELECT SUM(InOut*Price*Qty) 'All Inventory' 
        FROM home_transactions 
        WHERE (Type = 'Trade' OR Type = 'Purchase by Store') AND (DateOfSale BETWEEN '1992-12-31' AND (%s) || '-12-31')) + 
        (SELECT SUM(InOut*(Price/2)*Qty) 'All Sales' 
        FROM home_transactions 
        WHERE Type = 'Sales' AND (DateOfSale BETWEEN '1992-12-31' AND (%s) || '-12-31')) 'Ending Inventory'
    '''
    with connection.cursor() as cursor:
        cursor.execute(ending % (new_year, new_year))
        end_inv = cursor.fetchall()
    end_dols = []
    for dol in end_inv:
        end_dols.append(dol[0])
    cogs = beg_dols[0] + purchs[0] - end_dols[0]
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setTitle(f'COGS Report {year}')
    p.setFont('Helvetica-Bold', 30)
    p.drawCentredString(4.25*inch, 11*inch, f'Cost of Goods Sold {year}')
    p.line(1*inch, 10.9*inch, 7.5*inch, 10.9*inch)
    p.setFont('Helvetica', 20)
    p.drawString(1*inch, 10*inch, 'Beginning Inventory January 1, {}: ${:,.2f}'.format(year, beg_dols[0]))
    p.drawString(1 * inch, 9 * inch, '{} Purchases: ${:,.2f}'.format(year, purchs[0]))
    p.drawString(1 * inch, 8 * inch, 'Ending Inventory December 31, {}: ${:,.2f}'.format(year, end_dols[0]))
    p.drawString(1 * inch, 7 * inch, 'Cost of Goods Sold {}: ${:,.2f}'.format(year, cogs))
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, filename=f'COGS Report {year}.pdf')


# The views for the books
class BrowseBookListView(ListView):
    def get_queryset(self):
        query = self.request.GET.get('book')
        q = '''
        SELECT b."BookID", t."ID", a."AuthorID", tp."TopicID", b."Title", TRIM(a."FirstName" || ' ' || a."LastName") AS "Author", tp."Topic" AS "Genre"
        FROM home_books AS "b" JOIN home_transactions AS "t" ON b."BookID" = t."BookID" JOIN home_authors AS "a" ON b."AuthorID" = a."AuthorID" JOIN home_topics AS "tp" ON b."TopicID" = tp."TopicID"
        WHERE b."BookID" != 0 AND b."BookID" != 1 AND b."BookID" != 2 AND b."BookID" != 44 AND b."BookID" != 66 AND b."BookID" != 138 AND b."BookID" != 412 AND b."BookID" != 444 AND b."BookID" != 23780 
            AND b."BookID" != 74609 AND b."BookID" != 253302 {} 
        GROUP BY b."Title", tp."Topic", b."BookID", t."ID", a."AuthorID", tp."TopicID"
        HAVING SUM(t."Qty"*t."InOut") > 0
        ORDER BY 5;
        '''
        query = self.request.GET.get('book')
        if query is None:
            return Books.objects.raw(q.format(""))
        else:
            return Books.objects.raw(q.format('AND b."Title" ILIKE \''+ query.replace("'","") + '\''))

    def get_context_data(self, **kwargs):
        query = self.request.GET.get('book')
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        previousQuery = self.request.GET.get('book')
        if previousQuery is None:
            context['previousQuery'] = ""
        else:
            context['previousQuery'] = previousQuery
        return context

    model = Books
    template_name = 'home/browse.html'
    context_object_name = 'books'
    paginate_by = 12
class BookListView(ListView):
    def get_queryset(self):
        query = self.request.GET.get('book')
        if query is None:
            return Books.objects.order_by('Title')
        else:
            return Books.objects.filter(Title__icontains=query).order_by('Title')

    def get_context_data(self, **kwargs):   
        query = self.request.GET.get('book')
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        previousQuery = self.request.GET.get('book')
        if previousQuery is None:
            context['previousQuery'] = ""
        else:
            context['previousQuery'] = previousQuery
        return context

    model = Books
    template_name = 'home/browse.html'
    context_object_name = 'books'
    paginate_by = 12
class BookDetailView(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    model = Books
    template_name = 'home/books/detail.html'
    context_object_name = 'book'
class BookCreateView(LoginRequiredMixin, CreateView):
    model = Books
    fields = ['Title', 'CopyrightYear', 'PublisherID', 'SeriesID', 'AuthorID', 'TopicID', 'ISBN']
    template_name = 'home/books/create.html'
@login_required
def bookCreateView(req):
    if req.method == "POST":
        a = Books(Title=req.POST.get("title", ""),
                CopyrightYear=req.POST.get("copyrightYear", ""),
                PublisherID=Publishers.objects.filter(Publisher=req.POST.get("publisher", 'N/A'))[0],
                SeriesID=Series.objects.filter(Series=req.POST.get("series", 'None')),
                AuthorID=Authors.objects.filter(Q(LastName__icontains=req.POST.get("author", "N/A")) | Q(FirstName__icontains=req.POST.get("author", "N/A"))).order_by('LastName'),
                TopicID=Topics.objects.filter(Topic=req.POST.get("topic", "N/A")),
                ISBN=req.POST.get("ISBN", "000000000")
                )
        a.save()
        messages.add_message(req, messages.SUCCESS, 'Book created successfully!')
        return redirect("/browseall/")
    return render(req, 'home/books/_create.html')
class BookUpdateView(LoginRequiredMixin, UpdateView):
    model = Books
    fields = ['Title', 'CopyrightYear', 'PublisherID', 'SeriesID', 'AuthorID', 'TopicID', 'ISBN']
    template_name = 'home/books/create.html'
class BookDeleteView(LoginRequiredMixin, DeleteView):
    model = Books
    template_name = 'home/books/books_confirm_delete.html'
    success_url = "/browse/"


# The views for the authors
class AuthorListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        query = self.request.GET.get('author')
        if query is None:
            return Authors.objects.order_by('LastName')
        else:
            return Authors.objects.filter(Q(LastName__icontains=query) | Q(FirstName__icontains=query)).order_by('LastName')
    def get_context_data(self, **kwargs):   
        query = self.request.GET.get('author')
        context = super().get_context_data(**kwargs)
        previousQuery = self.request.GET.get('author')
        if previousQuery is None:
            context['previousQuery'] = ""
        else:
            context['previousQuery'] = previousQuery
        return context

    model = Authors
    template_name = 'home/authors/browse.html'
    context_object_name = 'authors'
    paginate_by = 15
class AuthorDetailView(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    redirect_field_name= 'redirect_to'
    model = Authors
    template_name = 'home/authors/detail.html'
    context_object_name = 'author'
@login_required
def authorCreateView(req):
    if req.method == "POST":
        a = Authors(FirstName=req.POST.get("firstName", ""),
                LastName=req.POST.get("lastName", ""),
                PrimaryTopic=Topics.objects.filter(Topic=req.POST.get("topicName", 'N/A'))[0])
        a.save()
        messages.add_message(req, messages.SUCCESS, 'Author created successfully!')
        return redirect("/authors/")
    return render(req, 'home/authors/_create.html')    
class AuthorUpdateView(LoginRequiredMixin, UpdateView):
    model = Authors
    fields = ['FirstName', 'LastName', 'PrimaryTopic', 'DateAdded']
    template_name = 'home/authors/create.html'
    context_object_name = 'author'
class AuthorDeleteView(LoginRequiredMixin, DeleteView):
    model = Authors
    template_name = 'home/authors/authors_confirm_delete.html'
    success_url = "/authors/"
    context_object_name = 'author'

# The views for the topics
class TopicListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        query = self.request.GET.get('topic')
        if query is None:
            return Topics.objects.order_by('TopicID')
        else:
            return Topics.objects.filter(Topic__icontains=query).order_by('TopicID')
    def get_context_data(self, **kwargs):   
        query = self.request.GET.get('Topic')
        context = super().get_context_data(**kwargs)
        previousQuery = self.request.GET.get('Topic')
        if previousQuery is None:
            context['previousQuery'] = ""
        else:
            context['previousQuery'] = previousQuery
        return context

    model = Topics
    template_name = 'home/topics/browse.html'
    context_object_name = 'topics'
    paginate_by = 15
class TopicDetailView(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    redirect_field_name= 'redirect_to'
    model = Topics
    template_name = 'home/topics/detail.html'
    context_object_name = 'topic'
class TopicCreateView(LoginRequiredMixin, CreateView):
    model = Topics
    fields = ['Topic']
    template_name = 'home/topics/create.html'
    success_url = '/topics/'
class TopicUpdateView(LoginRequiredMixin, UpdateView):
    model = Topics
    fields = ['Topic', 'DateAdded']
    template_name = 'home/topics/create.html'
    context_object_name = 'topic'
class TopicDeleteView(LoginRequiredMixin, DeleteView):
    model = Topics
    template_name = 'home/topics/topics_confirm_delete.html'
    success_url = "/topics/"


# The views for the transactions
class TransactionListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        query = self.request.GET.get('transaction')
        if query is None:
            return Transactions.objects.order_by('-DateOfSale')
        else:
            return Transactions.objects.filter(ID__icontains=query).order_by('ID')
    def get_context_data(self, **kwargs):   
        query = self.request.GET.get('transaction')
        context = super().get_context_data(**kwargs)
        previousQuery = self.request.GET.get('transaction')
        if previousQuery is None:
            context['previousQuery'] = ""
        else:
            context['previousQuery'] = previousQuery
        return context
    model = Transactions
    template_name = 'home/transactions/browse.html'
    context_object_name = 'transactions'
    paginate_by = 15
class TransactionDetailView(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    redirect_field_name= 'redirect_to'
    model = Transactions
    template_name = 'home/transactions/detail.html'
    context_object_name = 'transaction'
@login_required
def transactionCreateView(req):
    if req.method == "POST":
        t = Transactions(
                BookID=Books.objects.filter(Title=req.POST.get("book", ''))[0],
                Price=req.POST.get("price", 0),
                Resale=req.POST.get("resale", 0),
                TradePrice=req.POST.get("tradePrice", 0),
                Qty=req.POST.get("quantity", 1),
                TradeAllowed=req.POST.get("tradeAllowed", 1),
                #PercentTrade=req.POST.get("percentTrade", 0),
                CoverPrice=req.POST.get("coverPrice", 0),
                Discount=req.POST.get("discount", 0),
                NonTradex=req.POST.get("nonTradeX", 0),
                CoverID=CoverType.objects.filter(Cover=req.POST.get("cover", 'Paperback'))[0],
                LastUpdate=req.POST.get("lastUpdate", None),
                NoTradeAllowed=req.POST.get("noTradeAllowed", 1),
                TaxExempt=req.POST.get("taxExempt", 0),
                ConditionID=Conditions.objects.filter(Condition=req.POST.get("condition", 'Good'))[0],
                DateOfSale=req.POST.get("dateOfSale", ""),
                CustomerID=Customers.objects.filter(LastName=req.POST.get("customer", "Becky & David").split(",")[0])[0],
                #Tax=req.POST.get("tax", 0),
                Cash=req.POST.get("cash", 0),
                Check=req.POST.get("check", 0),
                CheckNum=req.POST.get("checkNo", 0),
                GiftCert=req.POST.get("giftCertificate", 0),
                Description=req.POST.get("description", ""),
                TaxRate=req.POST.get("taxRate", 0),
                SalesPerson=req.POST.get("salesPerson", "Becky"),
                Type=req.POST.get("type", ""),
                TradeCost=req.POST.get("tradeCost", 0),
                InOut=req.POST.get("inOut", 0),
                NonTradeY=req.POST.get("nonTradeY", 0),
                Labels=req.POST.get("labels", 0),
                )
        t.save()
        messages.add_message(req, messages.SUCCESS, 'Transaction created successfully!')
        return redirect("/transactions/")
    return render(req, 'home/transactions/_create.html')    
@login_required
def transactionUpdateView(req, pk):
    if req.method == "POST":
        Transactions.objects.filter(pk=req.POST.get("pk",0)).update(
            BookID=Books.objects.filter(Title=req.POST.get("book", ''))[0],
            Price=req.POST.get("price", 0),
            Resale=req.POST.get("resale", 0),
            TradePrice=req.POST.get("tradePrice", 0),
            Qty=req.POST.get("quantity", 1),
            TradeAllowed=req.POST.get("tradeAllowed", 1),
            #PercentTrade=req.POST.get("percentTrade", 0),
            CoverPrice=req.POST.get("coverPrice", 0),
            Discount=req.POST.get("discount", 0),
            NonTradex=req.POST.get("nonTradeX", 0),
            CoverID=CoverType.objects.filter(Cover=req.POST.get("cover", 'Paperback'))[0],
            LastUpdate=req.POST.get("lastUpdate", None),
            NoTradeAllowed=req.POST.get("noTradeAllowed", 1),
            TaxExempt=req.POST.get("taxExempt", 0),
            ConditionID=Conditions.objects.filter(Condition=req.POST.get("condition", 'Good'))[0],
            DateOfSale=req.POST.get("dateOfSale", ""),
            CustomerID=Customers.objects.filter(LastName=req.POST.get("customer", "Becky & David").split(",")[0])[0],
            #Tax=req.POST.get("tax", 0),
            Cash=req.POST.get("cash", 0),
            Check=req.POST.get("check", 0),
            CheckNum=req.POST.get("checkNo", 0),
            GiftCert=req.POST.get("giftCertificate", 0),
            Description=req.POST.get("description", ""),
            TaxRate=req.POST.get("taxRate", 0),
            SalesPerson=req.POST.get("salesPerson", "Becky"),
            Type=req.POST.get("type", ""),
            TradeCost=req.POST.get("tradeCost", 0),
            InOut=req.POST.get("inOut", 0),
            NonTradeY=req.POST.get("nonTradeY", 0),
            Labels=req.POST.get("labels", 0)
            )
        messages.add_message(req, messages.SUCCESS, 'Transaction updated successfully!')
        return redirect("/transactions/")
    t = Transactions.objects.get(pk=str(pk))
    context={
    'transaction': t
    }
    return render(req, 'home/transactions/_create.html', context)
class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transactions
    template_name = 'home/transactions/transactions_confirm_delete.html'
    success_url = "/transactions/"

# API views for AJAX queries
def getBookData(request):
    query = '''
        SELECT "BookID", TO_CHAR("DateAdded", 'Month') AS 'MonthAdded', TO_CHAR("DateAdded", 'YYYY') AS 'YearAdded', COUNT(*) AS 'COUNT'
        FROM home_books
        WHERE "DateAdded" >= current_date - interval '5' month
        GROUP BY TO_CHAR("DateAdded", 'YYYY'), TO_CHAR("DateAdded", 'Month');
    '''
    with connection.cursor() as cursor:
        cursor.execute(query)
        books = cursor.fetchall()
    bookList = []
    for book in books:
        bookList.append({'id': book[0], 'MonthAdded': book[1], 'YearAdded': book[2], 'count': book[3]})
    return HttpResponse(json.dumps(bookList), 'application/json')
def getTransactionData(request):
    time = request.GET.get('time', "day")
    query = f'''
        SELECT "ID", SUM("Price"), TO_CHAR("DateOfSale", 'YYYY'), TO_CHAR("DateOfSale", 'Month'), TO_CHAR("DateOfSale", 'DD')
        FROM home_transactions
        WHERE "DateOfSale" >= current_date - interval '7' {time}
        GROUP BY "DateOfSale"
        ORDER BY "DateOfSale";
    '''
    with connection.cursor() as cursor:
        cursor.execute(query)
        transactions = cursor.fetchall()

    transactionList = []
    for trans in transactions:
        transactionList.append({'id': trans[0], 'price': trans[1], 'year': trans[2], 'month': trans[3], 'day': trans[4]})
    return HttpResponse(json.dumps(transactionList), 'application/json')
def authorInput(request):
    lastnameInput = request.GET.get('text', '')
    if lastnameInput == "":
        return HttpResponse(json.dumps([]), 'application/json')
    query = f'''
        SELECT * FROM home_authors
        WHERE "LastName" ILIKE %s OR "FirstName" ILIKE %s
        LIMIT 5;
    '''
    authors = Authors.objects.raw(query, [lastnameInput + '%', lastnameInput + '%'])
    authorList = []
    for author in authors:
        authorList.append({'id': author.AuthorID, 'firstName': author.FirstName, 'lastName': author.LastName})
    return HttpResponse(json.dumps(authorList), 'application/json')
def topicInput(request):
    topicInput = request.GET.get('text', '')
    if topicInput == "":
        return HttpResponse(json.dumps([]), 'application/json')
    if "'" in topicInput:
        topicInput = topicInput.replace("'", "''")
    query = f"""
        SELECT * FROM home_topics
        WHERE "Topic" ILIKE %s
        LIMIT 5;
    """
    print(query)
    topics = Topics.objects.raw(query, [topicInput + '%'])
    print('\n\n'  + str(type(topics)) + '\n\n')
    print('\n\n'  + str(len(list(topics))) + '\n\n')

    topicList = []
    for topic in topics:
        topicList.append({'id': topic.TopicID, 'topic': topic.Topic})
    return HttpResponse(json.dumps(topicList), 'application/json')
def bookInput(request):
    bookInput = request.GET.get('text', '')
    if bookInput == "":
        return HttpResponse(json.dumps([]), 'application/json')
    if "'" in bookInput:
        bookInput = bookInput.replace("'", "''")
    query = f"""
        SELECT * FROM home_books
        WHERE "Title" ILIKE %s
        LIMIT 5;
    """
    books = Books.objects.raw(query, [bookInput + '%'])
    bookList = []
    for book in books:
        bookList.append({'id': book.BookID, 'title': book.Title})
    return HttpResponse(json.dumps(bookList), 'application/json')
def customerInput(request):
    customerInput = request.GET.get('text', '')
    if customerInput == "":
        return HttpResponse(json.dumps([]), 'application/json')
    if "'" in customerInput:
        customerInput = customerInput.replace("'", "''")
    query = f"""
        SELECT * FROM home_customers
        WHERE "LastName" ILIKE %s OR "FirstName" ILIKE %s
        LIMIT 5;
    """
    customers = Customers.objects.raw(query, [customerInput + '%', customerInput + '%'])
    customerList = []
    for customer in customers:
        customerList.append({'id': customer.CustomerID, 'firstName': customer.FirstName, 'lastName': customer.LastName})
    return HttpResponse(json.dumps(customerList), 'application/json')
def coverInput(request):
    coverInput = request.GET.get('text', '')
    if coverInput == "":
        return HttpResponse(json.dumps([]), 'application/json')
    if "'" in coverInput:
        coverInput = coverInput.replace("'", "''")
    query = f"""
        SELECT * FROM home_covertype
        WHERE "Cover" ILIKE %s
        LIMIT 5;
    """
    covers = CoverType.objects.raw(query, [coverInput + '%'])
    coverList = []
    for cover in covers:
        coverList.append({'id': cover.CoverID, 'cover': cover.Cover})
    return HttpResponse(json.dumps(coverList), 'application/json')
def conditionInput(request):
    conditionsInput = request.GET.get('text', '')
    if conditionsInput == "":
        return HttpResponse(json.dumps([]), 'application/json')
    if "'" in conditionsInput:
        conditionsInput = conditionsInput.replace("'", "''")
    query = f"""
        SELECT * FROM home_conditions
        WHERE "Condition" ILIKE %s
        LIMIT 5;
    """
    conditions = Conditions.objects.raw(query, [conditionsInput+'%'])
    conditionList = []
    for condition in conditions:
        conditionList.append({'id': condition.ConditionID, 'condition': condition.Condition})
    return HttpResponse(json.dumps(conditionList), 'application/json')
def publisherInput(request):
    publisherInput = request.GET.get('text', '')
    if publisherInput == "":
        return HttpResponse(json.dumps([]), 'application/json')
    if "'" in publisherInput:
        publisherInput = publisherInput.replace("'", "''")
    query = f"""
        SELECT * FROM home_publishers
        WHERE "Publisher" ILIKE %s
        LIMIT 5;
    """
    publishers = Publishers.objects.raw(query, [publisherInput+'%'])
    publisherList = []
    for publisher in publishers:
        publisherList.append({'id': publisher.PublisherID, 'publisher': publisher.Publisher})
    return HttpResponse(json.dumps(publisherList), 'application/json')
def seriesInput(request):
    seriesInput = request.GET.get('text', '')
    if seriesInput == "":
        return HttpResponse(json.dumps([]), 'application/json')
    if "'" in seriesInput:
        seriesInput = seriesInput.replace("'", "''")
    query = f"""
        SELECT * FROM home_series
        WHERE "Series" ILIKE %s
        LIMIT 5;
    """
    series = Series.objects.raw(query, seriesInput+'%')
    seriesList = []
    for s in series:
        seriesList.append({'id': s.SeriesID, 'series': s.Series})
    return HttpResponse(json.dumps(seriesList), 'application/json')

# The views for the Publishers
class PublisherListView(ListView):
    def get_queryset(self):
        query = self.request.GET.get('publisher')
        if query is None:
            return Publishers.objects.order_by('Publisher')
        else:
            return Publishers.objects.filter(Publisher__icontains=query).order_by('Publisher')

    def get_context_data(self, **kwargs):
        query = self.request.GET.get('publisher')
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        previousQuery = self.request.GET.get('publisher')
        if previousQuery is None:
            context['previousQuery'] = ""
        else:
            context['previousQuery'] = previousQuery
        return context

    model = Publishers
    template_name = 'home/publishers/browse.html'
    context_object_name = 'publishers'
    paginate_by = 15
class PublisherDetailView(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    model = Publishers
    template_name = 'home/publishers/detail.html'
    context_object_name = 'publisher'
class PublisherCreateView(LoginRequiredMixin, CreateView):
    model = Publishers
    fields = ['Publisher']
    template_name = 'home/publishers/create.html'
    success_url = '/publishers/'
class PublisherUpdateView(LoginRequiredMixin, UpdateView):
    model = Publishers
    fields = ['Publisher']
    template_name = 'home/publishers/create.html'
    success_url = '/publishers/'
class PublisherDeleteView(LoginRequiredMixin, DeleteView):
    model = Publishers
    template_name = 'home/publishers/publishers_confirm_delete.html'
    success_url = "/publishers/"
    context_object_name = 'publisher'


# The views for the Series
class SeriesListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        query = self.request.GET.get('series')
        if query is None:
            return Series.objects.order_by('Series')
        else:
            return Series.objects.filter(Q(Series__icontains=query)).order_by('Series')

    def get_context_data(self, **kwargs):
        query = self.request.GET.get('author')
        context = super().get_context_data(**kwargs)
        previousQuery = self.request.GET.get('series')
        if previousQuery is None:
            context['previousQuery'] = ""
        else:
            context['previousQuery'] = previousQuery
        return context

    model = Series
    template_name = 'home/series/browse.html'
    context_object_name = 'series'
    paginate_by = 15
class SeriesDetailView(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    model = Series
    template_name = 'home/series/detail.html'
    context_object_name = 'series'
class SeriesCreateView(LoginRequiredMixin, CreateView):
    model = Series
    fields = ['Series']
    template_name = 'home/series/create.html'
    success_url = '/series/'
class SeriesUpdateView(LoginRequiredMixin, UpdateView):
    model = Series
    fields = ['Series']
    template_name = 'home/series/create.html'
    context_object_name = 'series'
    success_url = '/series/'    
class SeriesDeleteView(LoginRequiredMixin, DeleteView):
    model = Series
    template_name = 'home/series/series_confirm_delete.html'
    success_url = "/series/"
    context_object_name = 'series'


# The views for the customers
class CustomerListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        query = self.request.GET.get('customer')
        if query is None:
            return Customers.objects.order_by('LastName')
        else:
            return Customers.objects.filter(Q(LastName__icontains=query) | Q(FirstName__icontains=query)).order_by(
                'LastName')

    def get_context_data(self, **kwargs):
        query = self.request.GET.get('customer')
        context = super().get_context_data(**kwargs)
        previousQuery = self.request.GET.get('customer')
        if previousQuery is None:
            context['previousQuery'] = ""
        else:
            context['previousQuery'] = previousQuery
        return context

    model = Customers
    template_name = 'home/customers/browse.html'
    context_object_name = 'customers'
    paginate_by = 15
class CustomerDetailView(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    model = Customers
    template_name = 'home/customers/detail.html'
    context_object_name = 'customer'
@login_required
def customersCreateView(req):
    if req.method == "POST":
        a = Customers(FirstName=req.POST.get("firstName", ""),
                      LastName=req.POST.get("lastName", ""),
                      Address=req.POST.get("address", ""),
                      City=req.POST.get("city", ""),
                      State=req.POST.get("state", ""),
                      Zip=req.POST.get("zip", ""),
                      HomePhone=req.POST.get("homePhone", ""),
                      Email=req.POST.get("email", ""))

        a.save()
        messages.add_message(req, messages.SUCCESS, 'Customer created successfully!')
        return redirect("/customers/")
    return render(req, 'home/customers/_create.html')
class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customers
    fields = ['FirstName', 'LastName', 'Address', 'City', 'State', 'Zip', 'HomePhone', 'DateAdded', 'Email']
    template_name = 'home/customers/_create.html'
    context_object_name = 'customer'
    success_url = '/customers/'
class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customers
    template_name = 'home/customers/customers_confirm_delete.html'
    success_url = "/customers/"
    context_object_name = 'customer'


# The views for the covers
class CoverListView(ListView):
    def get_queryset(self):
        query = self.request.GET.get('cover')
        if query is None:
            return CoverType.objects.order_by('Cover')
        else:
            return CoverType.objects.filter(Cover__icontains=query).order_by('Cover')

    def get_context_data(self, **kwargs):   
        query = self.request.GET.get('cover')
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        previousQuery = self.request.GET.get('cover')
        if previousQuery is None:
            context['previousQuery'] = ""
        else:
            context['previousQuery'] = previousQuery
        return context

    model = CoverType
    template_name = 'home/covers/browse.html'
    context_object_name = 'covers'
    paginate_by = 12
class CoverDetailView(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    model = CoverType
    template_name = 'home/covers/detail.html'
    context_object_name = 'cover'
class CoverCreateView(LoginRequiredMixin, CreateView):
    model = CoverType
    fields = ['Cover']
    template_name = 'home/covers/create.html'
    success_url = '/covers/' 
class CoverUpdateView(LoginRequiredMixin, UpdateView):
    model = CoverType
    fields = ['Cover']
    template_name = 'home/covers/create.html'
    success_url = '/covers/'
class CoverDeleteView(LoginRequiredMixin, DeleteView):
    model = CoverType
    template_name = 'home/covers/covers_confirm_delete.html'
    success_url = "/covers/"
    context_object_name = 'cover'