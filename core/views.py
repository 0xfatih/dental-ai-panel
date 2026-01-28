from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import Xray,Prediction
from django.contrib.auth.models import User
from django.db import IntegrityError
from  .ml.inference import predict_image
from pathlib import Path
from .ml.inference import draw_bboxes

def index(request):
    return render(request, "index.html")

@login_required
def upload_and_predict(request):
    if request.method == "POST":
        file = request.FILES.get("image")
        if not file:
            return render(request, "upload.html", {"error": "Dosya seç."})

        # 1️⃣ oluştur → pending
        xray = Xray.objects.create(
            user=request.user,
            image=file,
            status="pending"
        )

        try:
            preds = predict_image(
                weights_path=settings.YOLO_WEIGHTS_PATH,
                image_path=xray.image.path,
                conf=0.25
            )

            # 2️⃣ sonuç yok → failed
            if not preds:
                xray.status = "failed"
                xray.save(update_fields=["status"])
                return redirect("results", xray_id=xray.id)

            # 3️⃣ sonuç var → kaydet + done
            Prediction.objects.filter(xray=xray).delete()
            Prediction.objects.bulk_create([
                Prediction(
                    xray=xray,
                    label=p["label"],
                    score=p["score"],
                    x1=p["x1"], y1=p["y1"], x2=p["x2"], y2=p["y2"],
                )
                for p in preds
            ])

            xray.status = "done"
            xray.save(update_fields=["status"])
            return redirect("results", xray_id=xray.id)

        except Exception:
            xray.status = "failed"
            xray.save(update_fields=["status"])
            return redirect("results", xray_id=xray.id)

    return render(request, "upload.html")
        
@login_required
def tables(request):
    xrays = Xray.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "tables.html", {"xrays": xrays})

@login_required
def results(request, xray_id):
    xray = get_object_or_404(Xray, id=xray_id, user=request.user)
    predictions = Prediction.objects.filter(xray=xray)

    # Annotated image path
    annotated_dir = Path(settings.MEDIA_ROOT) / "annotated"
    annotated_dir.mkdir(exist_ok=True)

    annotated_path = annotated_dir / f"xray_{xray.id}.jpg"

    if not annotated_path.exists():
        draw_bboxes(
            image_path=xray.image.path,
            predictions=predictions,
            output_path=annotated_path
        )

    annotated_url = settings.MEDIA_URL + f"annotated/xray_{xray.id}.jpg"

    return render(request, "results.html", {
        "xray": xray,
        "predictions": predictions,
        "annotated_image": annotated_url,
    })

@login_required
def charts(request):
    return render(request, "charts.html")

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

def register_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name  = request.POST.get("last_name", "").strip()
        email      = request.POST.get("email", "").strip()
        username   = request.POST.get("username", "").strip()
        password   = request.POST.get("password", "").strip()

        if not (first_name and last_name and email and username and password):
            return render(request, "register.html", {
                "error": "Tüm alanları doldur."
            })

        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
        except IntegrityError:
            return render(request, "register.html", {
                "error": "Bu kullanıcı adı zaten kullanılıyor."
            })

        return redirect("login")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            next_url = request.GET.get("next")  # login_required buraya yönlendirir
            return redirect(next_url or "index")

        return render(request, "login.html", {"error": "Kullanıcı adı veya şifre hatalı."})

    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("index")

def privacy(request):
    return render(request, "privacy.html")

def terms(request):
    return render(request, "terms.html")

def yolov11(request):
    return render(request, "yolov11.html")

@login_required
def results_pdf(request, xray_id):
    xray = get_object_or_404(Xray, id=xray_id, user=request.user)
    predictions = Prediction.objects.filter(xray=xray)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="xray_report_{xray.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Başlık
    elements.append(Paragraph("<b>Dental AI Analysis Report</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"User: {xray.user.username}", styles["Normal"]))
    elements.append(Paragraph(f"Date: {xray.created_at.strftime('%d.%m.%Y %H:%M')}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Görsel (annotated varsa onu al)
    annotated_path = Path(settings.MEDIA_ROOT) / "annotated" / f"xray_{xray.id}.jpg"
    image_path = annotated_path if annotated_path.exists() else Path(xray.image.path)

    elements.append(Image(str(image_path), width=400, height=300))
    elements.append(Spacer(1, 20))

    # Tablo
    table_data = [["#", "Disease", "Confidence (%)"]]
    for i, p in enumerate(predictions, start=1):
        score = p.score * 100 if p.score <= 1 else p.score
        table_data.append([i, p.label, f"{score:.2f}"])

    table = Table(table_data, colWidths=[40, 200, 120])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # Legend
    elements.append(Paragraph("<b>Legend</b>", styles["Heading2"]))

    legend = [
        ["Caries", "Red"],
        ["Filling", "Blue"],
        ["Crown / Bridge", "Purple"],
        ["Implant", "Green"],
        ["Post-screw", "Yellow"],
        ["Root Canal Obturation", "Orange"],
    ]

    legend_table = Table(legend, colWidths=[200, 160])
    legend_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
    ]))

    elements.append(legend_table)

    doc.build(elements)
    return response


