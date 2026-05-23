<#import "template.ftl" as layout>
<@layout.registrationLayout displayMessage=!messagesPerField.existsError('username','password'); section>
    <#if section = "header">
        Area de Administração
    <#elseif section = "form">
        <style>
            .tacaua-branding {
                text-align: center;
                margin-bottom: 8px;
            }
            .tacaua-branding-title {
                font-size: 1.75rem;
                font-weight: 700;
                color: #0d9488;
                margin: 0 0 4px 0;
            }
            .tacaua-branding-subtitle {
                font-size: 0.875rem;
                color: #6b7280;
                margin: 0 0 24px 0;
            }
            #kc-form-login input[type="text"],
            #kc-form-login input[type="password"] {
                background-color: #e5e7eb;
            }
        </style>
        <#if realm.password>
            <form id="kc-form-login" onsubmit="login.disabled = true; return true;" action="${url.loginAction}" method="post">

                <div class="${properties.kcFormGroupClass!}">
                    <label for="username" class="${properties.kcLabelClass!}">
                        <#if !realm.loginWithEmailAllowed>
                            ${msg("username")}
                        <#elseif !realm.registrationEmailAsUsername>
                            ${msg("usernameOrEmail")}
                        <#else>
                            ${msg("email")}
                        </#if>
                    </label>
                    <input
                        tabindex="1"
                        id="username"
                        class="${properties.kcInputClass!}"
                        name="username"
                        value="${(login.username!'')}"
                        type="text"
                        autofocus
                        autocomplete="username"
                        aria-invalid="<#if messagesPerField.existsError('username','password')>true</#if>"
                    />
                    <#if messagesPerField.existsError('username','password')>
                        <span id="input-error" class="${properties.kcInputErrorMessageClass!}" aria-live="polite">
                            ${kcSanitize(messagesPerField.getFirstError('username','password'))?no_esc}
                        </span>
                    </#if>
                </div>

                <div class="${properties.kcFormGroupClass!}">
                    <label for="password" class="${properties.kcLabelClass!}">${msg("password")}</label>
                    <input
                        tabindex="2"
                        id="password"
                        class="${properties.kcInputClass!}"
                        name="password"
                        type="password"
                        autocomplete="current-password"
                        aria-invalid="<#if messagesPerField.existsError('username','password')>true</#if>"
                    />
                </div>

                <div class="${properties.kcFormGroupClass!} ${properties.kcFormSettingClass!}">
                    <div id="kc-form-options">
                        <#if realm.rememberMe && !usernameEditDisabled??>
                            <div class="checkbox">
                                <label>
                                    <#if login.rememberMe??>
                                        <input tabindex="3" id="rememberMe" name="rememberMe" type="checkbox" checked> ${msg("rememberMe")}
                                    <#else>
                                        <input tabindex="3" id="rememberMe" name="rememberMe" type="checkbox"> ${msg("rememberMe")}
                                    </#if>
                                </label>
                            </div>
                        </#if>
                    </div>
                    <div class="${properties.kcFormOptionsWrapperClass!}">
                        <#if realm.resetPasswordAllowed>
                            <span><a tabindex="5" href="${url.loginResetCredentialsUrl}">${msg("doForgotPassword")}</a></span>
                        </#if>
                    </div>
                </div>

                <div id="kc-form-buttons" class="${properties.kcFormGroupClass!}" style="display:flex;gap:8px;align-items:stretch;">
                    <input type="hidden" id="id-hidden-input" name="credentialId" <#if auth.selectedCredential?has_content>value="${auth.selectedCredential}"</#if>/>
                    <a href="/" style="flex:1;display:flex;align-items:center;justify-content:center;border:1.5px solid #0d9488;border-radius:6px;color:#0d9488;text-decoration:none;font-size:1.1rem;transition:background-color 0.15s,color 0.15s;" onmouseover="this.style.backgroundColor='#0d9488';this.style.color='#fff'" onmouseout="this.style.backgroundColor='transparent';this.style.color='#0d9488'">&#8592;</a>
                    <div style="flex:7;">
                        <input
                            tabindex="4"
                            class="${properties.kcButtonClass!} ${properties.kcButtonPrimaryClass!} ${properties.kcButtonBlockClass!} ${properties.kcButtonLargeClass!}"
                            name="login"
                            id="kc-login"
                            type="submit"
                            value="${msg("doLogIn")}"
                            style="width:100%;"
                        />
                    </div>
                </div>
            </form>
        </#if>
    </#if>
</@layout.registrationLayout>
