from django.urls import path

from . import views
from . import advanced_views


urlpatterns = [

    # =====================================================
    # HEALTH CHECK
    # Used by Render to verify the service is alive.
    # =====================================================

    path(
        "health/",
        views.health_check,
        name="health_check",
    ),


    # =====================================================
    # 0. PUBLIC GOVERNMENT PORTAL HOMEPAGE & ABOUT
    # =====================================================

    path(
        "",
        views.home_portal,
        name="home",
    ),

    path(
        "about/",
        views.about_view,
        name="about",
    ),

    # =====================================================
    # 0.1 INTER-CPSE MATERIAL TRANSFER
    # =====================================================

    path(
        "transfer/",
        views.material_transfer_view,
        name="material_transfer",
    ),

    # =====================================================
    # 1. CONTROL CENTER / OPERATIONAL WORKSPACE
    # =====================================================

    path(
        "workspace/",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard_alias",
    ),



    # =====================================================
    # 2. MATERIAL INTELLIGENCE
    # DOCUMENT INGESTION / OCR / EXTRACTION
    # =====================================================

    path(
        "extract/",
        views.document_ingest,
        name="document_ingest",
    ),


    # =====================================================
    # 3. MATERIAL COMPARATOR
    # =====================================================

    path(
        "comparator/",
        views.compare_materials_view,
        name="comparator",
    ),

    path(
        "comparator/feedback/",
        views.record_comparator_feedback,
        name="record_comparator_feedback",
    ),


    # =====================================================
    # 4. DIGITAL COMPLIANCE TWIN
    # =====================================================

    path(
        "compliance/",
        advanced_views.compliance_view,
        name="compliance",
    ),


    # =====================================================
    # 5. FINANCIAL SAVINGS + CARBON
    # =====================================================

    path(
        "savings/",
        advanced_views.savings_view,
        name="savings",
    ),


    # =====================================================
    # 6. PROCUREMENT INTELLIGENCE
    # =====================================================

    path(
        "procurement/",
        advanced_views.procurement_view,
        name="procurement",
    ),


    # =====================================================
    # 7. CAD / 3D MATCHER
    # =====================================================

    path(
        "cad/",
        advanced_views.cad_view,
        name="cad_matcher",
    ),


    # =====================================================
    # 8. MULTILINGUAL INGESTION
    # =====================================================

    path(
        "multilingual/",
        advanced_views.multilingual_view,
        name="multilingual",
    ),


    # =====================================================
    # 9. DATA LINEAGE
    # =====================================================

    path(
        "lineage/",
        advanced_views.lineage_view,
        name="data_lineage",
    ),


    # =====================================================
    # 10. AUDIT + GOVERNANCE
    # =====================================================

    path(
        "audit/",
        views.audit_trail,
        name="audit_trail",
    ),
    path(
        "audit_trail/",
        views.audit_trail,
        name="audit_trail_alias",
    ),


    # =====================================================
    # 11. CANDIDATE GROUPS
    # =====================================================

    path(
        "groups/<int:group_id>/",
        views.group_detail,
        name="group_detail",
    ),


    # =====================================================
    # 12. NATIONAL MATERIAL MASTER
    # =====================================================

    path(
        "national-master/",
        views.national_master,
        name="national_master",
    ),

    path(
        "national-master/<int:material_id>/",
        views.national_material_detail,
        name="national_material_detail",
    ),

    path(
        "national-master/<int:material_id>/review/",
        views.review_national_material,
        name="review_national_material",
    ),


    # =====================================================
    # 13. SOURCE CATALOGUE
    # =====================================================

    path(
        "catalogue/",
        views.source_catalogue,
        name="source_catalogue",
    ),

    path(
        "catalogue/<int:material_id>/",
        views.material_detail,
        name="material_detail",
    ),


    # =====================================================
    # 14. ADVANCED INTELLIGENCE HUB
    # =====================================================

    path(
        "advanced/",
        advanced_views.advanced_center,
        name="advanced_center",
    ),


    # =====================================================
    # 15. ERP DUPLICATE DETECTOR API
    # =====================================================

    path(
        "api/erp-duplicate-check/",
        advanced_views.erp_duplicate_api,
        name="erp_duplicate_api",
    ),


    # =====================================================
    # 16. GLOBAL MATERIAL SEARCH
    # =====================================================

    path(
        "search/",
        views.search_materials,
        name="search",
    ),


    # =====================================================
    # 17. ENGINEERING REVIEW WORKBENCH
    # =====================================================

    path(
        "review/workbench/",
        views.review_workbench,
        name="review_workbench",
    ),
    path(
        "review/",
        views.review_workbench,
        name="review_workbench_alias",
    ),


    # =====================================================
    # 18. ENGINEER AUTHENTICATION (PROTOTYPE)
    # =====================================================

    path(
        "auth/login/",
        views.engineer_login,
        name="engineer_login",
    ),
    path(
        "login/",
        views.engineer_login,
        name="login",
    ),

    path(
        "auth/logout/",
        views.engineer_logout,
        name="engineer_logout",
    ),
    path(
        "logout/",
        views.engineer_logout,
        name="logout",
    ),

    path(
        "auth/setup-demo/",
        views.create_demo_user,
        name="create_demo_user",
    ),

]