import uuid
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.timezone import now as timezone_now
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.contrib.auth.forms import SetPasswordForm
from .models import CustomUser
from inventory.models import Product, Category, ProductMovement
from django.views.decorators.cache import cache_page
from .models import Message 
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.conf import settings

User = get_user_model()
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'








@cache_page(60 * 15)
@login_required
def dashboard_view(request):
    if request.user.role not in ['admin', 'employee']:
        return HttpResponseForbidden("Accès réservé aux utilisateurs autorisés.")

    today = timezone.now().date()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]

    chart_data = []
    chart_labels = []
    for day in last_7_days:
        movement_count = ProductMovement.objects.filter(date__date=day).count()
        chart_data.append(movement_count)
        chart_labels.append(day.strftime("%a %d"))

    total_capacity = 1000

    products = list(Product.objects.all())
    total_stock = sum(p.quantity for p in products)
    stock_percentage = min(round((total_stock / total_capacity) * 100, 2), 100)

    low_stock_count = sum(1 for p in products if p.quantity < 5)
    well_stocked_count = len(products) - low_stock_count

    products_sorted = sorted(products, key=lambda x: x.quantity, reverse=True)[:10]
    product_names = [p.name for p in products_sorted]
    product_quantities = [p.quantity for p in products_sorted]

    context = {
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'stock_percentage': stock_percentage,
        'total_stock': total_stock,
        'total_capacity': total_capacity,
        'today_movements': ProductMovement.objects.filter(date__date=today).count(),
        'low_stock_count': low_stock_count,
        'well_stocked_count': well_stocked_count,
        'recent_products': sorted(products, key=lambda x: x.created_at, reverse=True)[:8], 
        'user_photo': request.user.photo.url if request.user.photo else None,
        'user_name': request.user.full_name,
        'user_role': request.user.role,
        'total_products': len(products),
        'total_categories': Category.objects.count(),
        'product_names': product_names,
        'product_quantities': product_quantities,
    }

    return render(request, 'dashboard/dashboard.html', context)





@login_required
def invite_user_view(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Seul l'administrateur peut inviter des utilisateurs.")

    if request.method == 'POST':
        try:
            full_name = request.POST.get('full_name')
            email = request.POST.get('email')
            role = request.POST.get('role')
            
            if not all([full_name, email, role]):
                messages.error(request, "Tous les champs obligatoires doivent être remplis.")
                return redirect('invite_user')

            if role not in ['admin', 'employee']:
                messages.error(request, "Rôle invalide.")
                return redirect('invite_user')

            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "Email déjà utilisé.")
                return redirect('invite_user')

            invitation_token = uuid.uuid4()
            token_expiry = timezone_now() + timedelta(days=2)

            user = CustomUser.objects.create(
                full_name=full_name,
                email=email,
                role=role,
                is_active=True,
                invitation_token=invitation_token,
                token_expiry=token_expiry,
                password=str(uuid.uuid4())  
            )

         
            invite_link = request.build_absolute_uri(
                reverse('set_password', args=[str(invitation_token)])
            )

            try:
                send_mail(
                    subject="Invitation à rejoindre notre plateforme",
                    message=(
                        f"Bonjour {full_name},\n\n"
                        f"Vous avez été invité(e) à rejoindre notre plateforme en tant que {role}.\n\n"
                        f"Pour activer votre compte et définir votre mot de passe, cliquez sur le lien suivant :\n"
                        f"{invite_link}\n\n"
                        f"Ce lien expirera le {token_expiry.strftime('%d/%m/%Y à %H:%M')}.\n\n"
                        "Cordialement,\nL'équipe technique"
                    ),
                    from_email=None, 
                    recipient_list=[email],
                    fail_silently=False
                )
                messages.success(request, f"Invitation envoyée à {email}")
                return redirect('dashboard')
                
            except Exception as e:
                user.delete()  
                messages.error(request, f"Erreur lors de l'envoi de l'email: {str(e)}")
                return redirect('invite_user')

        except Exception as e:
            messages.error(request, f"Une erreur est survenue: {str(e)}")
            return redirect('invite_user')

    return render(request, 'dashboard/users/invite_user.html')


def accept_invitation_view(request, token):
    user = get_object_or_404(CustomUser, invitation_token=token)
    
    if timezone_now() > user.token_expiry:
        messages.error(request, "Lien expiré. Contactez l'administrateur.")
        return redirect('login')

    if request.method == 'POST':
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('accept_invitation', token=token)
            
        user.set_password(password)
        user.invitation_token = None
        user.token_expiry = None
        user.is_active = True
        user.first_login = True  
        user.save()
        
        messages.success(request, "Compte activé ! Connectez-vous maintenant.")
        return redirect('login') 


def set_password_view(request, token):
    user = get_object_or_404(CustomUser, invitation_token=token)

    if timezone_now() > user.token_expiry:
        messages.error(request, "Le lien d'invitation a expiré.")
        return redirect('login')

    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not password1 or not password2:
            messages.error(request, "Veuillez remplir les deux champs.")
            return redirect(request.path)

        if password1 != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect(request.path)

        user.password = make_password(password1)
        user.invitation_token = None
        user.token_expiry = None
        user.save()

        messages.success(request, "Mot de passe défini avec succès, vous pouvez maintenant vous connecter.")
        return redirect('login')

    return render(request, 'dashboard/users/set_password.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "Veuillez remplir tous les champs")
            return render(request, 'users/login.html')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Connexion réussie", extra_tags="login success")
            return redirect('login') 
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")

    return render(request, 'users/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')





















@login_required
def profile_settings_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        bio = request.POST.get('bio')
        photo = request.FILES.get('photo')
        
        user = request.user
        user.full_name = full_name
        user.phone_number = phone_number
        user.bio = bio
        if photo:
            user.photo = photo
        user.profile_complete = True 
        user.save()
        
        messages.success(request, "Profil mis à jour avec succès!")
        return redirect('dashboard')
    
    return render(request, 'dashboard/users/profile_settings.html')

@login_required
def user_list(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("Seul l'administrateur peut accéder à cette page.")

    users = CustomUser.objects.all()
    return render(request, 'dashboard/users/user_list.html', {'users': users})

@login_required
def user_detail(request, pk):
    if not is_admin(request.user):
        return HttpResponseForbidden("Seul l'administrateur peut accéder à cette page.")

    user = get_object_or_404(CustomUser, id=pk)
    return render(request, 'dashboard/users/user_detail.html', {'user': user})

@login_required
def user_edit(request, pk):
    if not is_admin(request.user):
        return HttpResponseForbidden("Seul l'administrateur peut accéder à cette page.")

    user = get_object_or_404(CustomUser, id=pk)

    if request.method == 'POST':
        user.full_name = request.POST.get('full_name')
        user.email = request.POST.get('email')
        user.role = request.POST.get('role')
        user.phone_number = request.POST.get('phone_number')
        user.bio = request.POST.get('bio')
        photo = request.FILES.get('photo')
        if photo:
            user.photo = photo
        user.save()
        
        messages.success(request, "Utilisateur mis à jour avec succès!")
        return redirect('user_list')

    return render(request, 'dashboard/users/user_edit.html', {'user': user})
@login_required
def user_delete(request, pk):
    if not is_admin(request.user):
        return HttpResponseForbidden("Seul l'administrateur peut accéder à cette page.")

    user = get_object_or_404(CustomUser, id=pk)

    if request.method == 'POST':
        user.delete()
        messages.success(request, "Utilisateur supprimé avec succès!")
        return redirect('user_list')

    return render(request, 'dashboard/users/user_delete.html', {'user': user})











@login_required
def inbox(request):
    messages = Message.objects.filter(receiver=request.user) | Message.objects.filter(sender=request.user)
    messages = messages.order_by("timestamp")

    if request.method == "POST":
        receiver_id = request.POST.get("receiver")
        content = request.POST.get("content")

        if receiver_id and content:
            receiver = User.objects.get(id=receiver_id)
            Message.objects.create(sender=request.user, receiver=receiver, content=content)
            return redirect("inbox")

    users = User.objects.exclude(id=request.user.id)  
    return render(request, "dashboard/users/inbox.html", {"messages": messages, "users": users})






def password_reset_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            form.save(
                request=request,
                use_https=request.is_secure(),
                from_email=settings.DEFAULT_FROM_EMAIL,
                email_template_name='users/password_reset_email.html',
                subject_template_name='users/password_reset_subject.txt'
            )
            
            messages.success(request, "Email de réinitialisation envoyé.")
            return redirect('password_reset_done')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = PasswordResetForm()
    
    return render(request, 'dashboard/users/password_reset.html', {'form': form})

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'dashboard/users/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'dashboard/users/password_reset_confirm.html'
    form_class = SetPasswordForm
    
    def form_valid(self, form):
        messages.success(self.request, "Votre mot de passe a été réinitialisé avec succès.")
        return super().form_valid(form)

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'dashboard/users/password_reset_complete.html'