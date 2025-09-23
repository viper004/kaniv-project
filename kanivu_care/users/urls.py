from django.urls import path

from users import views

app_name="users"

urlpatterns=[
    path("register/",views.Register,name="register"),
    path("num_verify/",views.numVerify,name="num_verify"),
    path("resend_otp/",views.resendOTP,name="resend_otp"),
    path("login/",views.Login,name="login"),
    path("logout/",views.Logout,name="logout"),
    path("profile/",views.Profile,name="profile"),
    path("forgot_password/",views.forgotPassword,name="forgot_password"),
    path("update/",views.UpdateProfile,name="update"),
    path("verify_number/",views.verifyPhoneNumber,name="verify_number"),
    path("update_phone_number/",views.updatePhoneNumber,name="update_phone_number"),
    path("verify_email/",views.verifyEmail,name="verify_email"),
    path("update_email/",views.updateEmail,name="update_email"),
    path("update_password/",views.updatePassword,name="update_password"),
    path("delete_account/",views.deleteAccount,name="delete_account"),
    path("academic_edit/",views.editAcademic,name="academic_edit"),




]