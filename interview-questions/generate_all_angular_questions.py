import os
import html

def get_angular_questions():
    questions = []

    # Q1: ChangeDetectionStrategy.OnPush & Object Mutability
    questions.append({
        "id": 1,
        "badge": "Change Detection & Performance",
        "keywords": "change detection onpush mutability reference equality zonejs markforcheck spread",
        "concept": "ChangeDetectionStrategy.OnPush, strict reference equality checks (<code>===</code>), object/array in-place mutability traps, and immutable state updates.",
        "question": """A developer optimizes an enterprise data grid by adding <code>changeDetection: ChangeDetectionStrategy.OnPush</code>. Look at the component code snippet.
<br><br>
<strong>Part A:</strong> When the user clicks \"Add Item\", the item is pushed into the array, but the UI table fails to display the new item. Why does <code>ChangeDetectionStrategy.OnPush</code> ignore in-place array mutations like <code>items.push()</code>?
<br>
<strong>Part B:</strong> What three triggers cause an <code>OnPush</code> component to re-evaluate its template?
<br>
<strong>Part C:</strong> How do you fix this using immutable state spread operators, and what is the difference between <code>ChangeDetectorRef.detectChanges()</code> versus <code>ChangeDetectorRef.markForCheck()</code>?""",
        "snippet_title": "order-list.component.ts",
        "snippet_code": """@Component({
  selector: 'app-order-list',
  standalone: true,
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <button (click)="addItem()">Add Item</button>
    <ul>
      <li *ngFor="let item of items">{{ item.name }}</li>
    </ul>
  `
})
export class OrderListComponent {
  @Input() items: Item[] = [];

  addItem() {
    this.items.push({ id: Date.now(), name: 'New Item' });
  }
}""",
        "rating_concept": "ChangeDetectionStrategy.OnPush, reference equality, and markForCheck vs detectChanges",
        "solution": """<strong>Part A (Reference Equality & The Mutability Trap):</strong>
<br>• Under default change detection, Zone.js checks every component on every asynchronous event by dirty-checking values.
<br>• Under <code>ChangeDetectionStrategy.OnPush</code>, Angular skips the component subtree unless its <strong>inputs change by object reference</strong> (evaluated via <code>Object.is(oldVal, newVal)</code> / <code>===</code>).
<br>• <code>this.items.push(...)</code> mutates the existing array in-place: the array memory reference remains <strong>identical</strong> (<code>oldItems === newItems</code>).
<br>• Angular assumes nothing has changed and skips template re-rendering.
<br><br>
<strong>Part B (The 3 Triggers of OnPush Change Detection):</strong>
<br>1. An <code>@Input()</code> property reference changes to a new object or primitive.
<br>2. An event originates directly from the component itself or one of its children (e.g. <code>(click)</code>, <code>(keyup)</code>).
<br>3. An explicit call is made to <code>ChangeDetectorRef.markForCheck()</code> (or an <code>async</code> pipe / Signal emits a new value).
<br><br>
<strong>Part C (Immutable Spread & markForCheck vs detectChanges):</strong>
<br>• <strong>Fix:</strong> Create a new array reference: <code>this.items = [...this.items, newItem];</code>.
<br>• <code>markForCheck()</code>: Marks the component and all its ancestors up to the root as dirty, requesting a pass during the <em>next</em> scheduled change detection cycle.
<br>• <code>detectChanges()</code>: Runs change detection synchronously on the component and its children <em>immediately</em>, which can cause <code>ExpressionChangedAfterItHasBeenCheckedError</code> if abused.""",
        "optimized_code": """addItem() {
  const newItem = { id: Date.now(), name: 'New Item' };
  this.items = [...this.items, newItem]; // New reference triggers OnPush
}""",
        "junior_eval": "Removes ChangeDetectionStrategy.OnPush to go back to Default change detection or injects ChangeDetectorRef and calls detectChanges() on every event.",
        "expert_eval": "Explains reference equality checking (Object.is), enforces immutable state updates with array spread, and clearly contrasts markForCheck() with detectChanges()."
    })

    # Q2: Angular Signals vs RxJS Observables
    questions.append({
        "id": 2,
        "badge": "Reactivity Architecture (v16–v18)",
        "keywords": "signals rxjs computed effect glitch free tosignal toobservable zonejs",
        "concept": "Fine-grained reactivity with Angular Signals (<code>signal</code>, <code>computed</code>, <code>effect</code>), glitch-free synchronous dependency tracking, and interoperability with RxJS (<code>toSignal</code>, <code>toObservable</code>).",
        "question": """An e-commerce checkout page manages cart items, discount codes, and taxes using Angular 17/18 Signals. Look at the code snippet.
<br><br>
<strong>Part A:</strong> What is the core architectural difference between <strong>Angular Signals</strong> (synchronous value containers with dependency tracking) and <strong>RxJS Observables</strong> (asynchronous push-based streams)?
<br>
<strong>Part B:</strong> Look at the <code>computed()</code> block in the code. Why is calling <code>taxAmount.set(...)</code> inside a <code>computed()</code> strictly forbidden by the Angular compiler, throwing <code>NG0600: Writing to signals is not allowed in a computed</code>?
<br>
<strong>Part C:</strong> When should an architect mandate RxJS over Signals, and when should Signals replace RxJS in modern application components?""",
        "snippet_title": "cart-state.service.ts",
        "snippet_code": """@Injectable({ providedIn: 'root' })
export class CartStateService {
  cartItems = signal<CartItem[]>([]);
  taxRate = signal<number>(0.08);
  taxAmount = signal<number>(0);

  subtotal = computed(() => {
    return this.cartItems().reduce((acc, item) => acc + item.price, 0);
  });

  total = computed(() => {
    const calcTax = this.subtotal() * this.taxRate();
    this.taxAmount.set(calcTax);
    return this.subtotal() + calcTax;
  });
}""",
        "rating_concept": "Angular Signals, computed purity, side-effect elimination, and Signals vs RxJS",
        "solution": """<strong>Part A (Signals vs Observables Comparison):</strong>
<br>• <strong>Signals:</strong> Synchronous state primitives with <strong>pull-based evaluation</strong> and dynamic dependency tracking. They always have a current value, execute glitch-free (eliminating diamond dependency problems), and enable fine-grained DOM updates without Zone.js.
<br>• <strong>RxJS Observables:</strong> Push-based asynchronous streams over time. Required for complex event coordination (debouncing, race conditions, cancellation via <code>switchMap</code>, retry logic, WebSockets).
<br><br>
<strong>Part B (Computed Signal Purity & NG0600):</strong>
<br>• <code>computed()</code> signals are strictly designed to be <strong>pure derivation functions</strong>.
<br>• Writing to another signal inside a <code>computed</code> derivation introduces side effects, which can cause cyclic dependency loops and unpredictable rendering order.
<br>• <code>taxAmount</code> should simply be another derived <code>computed()</code> signal, not a writable signal updated as a side effect.
<br><br>
<strong>Part C (When to Use What):</strong>
<br>• <em>Use Signals for:</em> Synchronous UI component state, derived values, inputs, queries, and replacing Zone.js for change detection.
<br>• <em>Use RxJS for:</em> HTTP calls, debounced search inputs, WebSocket real-time feeds, interval polling, and complex asynchronous stream composition.""",
        "optimized_code": """@Injectable({ providedIn: 'root' })
export class CleanCartService {
  cartItems = signal<CartItem[]>([]);
  taxRate = signal<number>(0.08);

  subtotal = computed(() => 
    this.cartItems().reduce((acc, item) => acc + item.price, 0)
  );

  taxAmount = computed(() => this.subtotal() * this.taxRate());

  total = computed(() => this.subtotal() + this.taxAmount());
}""",
        "junior_eval": "Uses an effect() or setTimeout to bypass the computed() mutation check, unaware of reactivity graph purity and cyclic dependency loops.",
        "expert_eval": "Articulates pull-based fine-grained reactivity, refactors side-effects into pure computed derivations, and defines clean boundaries between Signals (state) and RxJS (async events)."
    })

    # Q3: RxJS Subscription Memory Leaks & takeUntilDestroyed
    questions.append({
        "id": 3,
        "badge": "Memory Management & Lifecycle",
        "keywords": "rxjs subscription memory leak takeuntildestroyed destroyref async pipe closure",
        "concept": "RxJS Observable subscription memory leaks, garbage collection retention through closures, <code>takeUntilDestroyed</code>, <code>DestroyRef</code>, and declarative <code>async</code> pipe.",
        "question": """A single-page dashboard navigates between multiple views. Look at the component code snippet.
<br><br>
<strong>Part A:</strong> A user navigates back and forth between the Dashboard and Settings 20 times. Profiling in Chrome DevTools shows 20 active component instances retained in heap memory and 20 simultaneous HTTP calls on every event. Explain how this memory leak occurs.
<br>
<strong>Part B:</strong> How does Angular 16+ <code>takeUntilDestroyed</code> eliminate subscription leaks without requiring <code>ngOnDestroy()</code> and boilerplate <code>Subject</code> tear-downs?
<br>
<strong>Part C:</strong> What is the injection context requirement of <code>takeUntilDestroyed()</code>, and how do you use it if subscribing inside a lifecycle hook like <code>ngOnInit()</code>?""",
        "snippet_title": "dashboard-metrics.component.ts",
        "snippet_code": """@Component({
  selector: 'app-dashboard-metrics',
  standalone: true,
  template: `<div>Live Users: {{ activeUsers }}</div>`
})
export class DashboardMetricsComponent implements OnInit {
  activeUsers = 0;

  constructor(private metricsService: MetricsService) {}

  ngOnInit() {
    this.metricsService.userStream$.subscribe(users => {
      this.activeUsers = users.length;
    });
  }
}""",
        "rating_concept": "RxJS subscription memory leaks, takeUntilDestroyed, DestroyRef, and injection contexts",
        "solution": """<strong>Part A (Closure Scope Retaining Component Instances):</strong>
<br>• <code>metricsService</code> is a singleton service that lives for the entire application lifetime.
<br>• When <code>subscribe()</code> is called in <code>DashboardMetricsComponent</code>, the callback closure captures <code>this</code> (the component instance).
<br>• When the user navigates away, the component view is removed from the DOM, but the singleton service retains a direct reference to the component instance in its observer list.
<br>• The Garbage Collector <strong>cannot free the component</strong>, leading to massive memory leaks, duplicate callbacks, and stale event executions.
<br><br>
<strong>Part B (takeUntilDestroyed via DestroyRef):</strong>
<br>• <code>takeUntilDestroyed</code> automatically hooks into Angular's <code>DestroyRef</code>.
<br>• When the component or injector is destroyed, the operator automatically emits a completion signal and unregisters the subscription, releasing memory.
<br><br>
<strong>Part C (Injection Context Requirement):</strong>
<br>• If called in the <code>constructor()</code>, <code>takeUntilDestroyed()</code> automatically infers the <code>DestroyRef</code> from the active injection context.
<br>• If called in <code>ngOnInit()</code>, the constructor injection context has ended. You must explicitly inject <code>DestroyRef</code> and pass it: <code>takeUntilDestroyed(this.destroyRef)</code>.""",
        "optimized_code": """@Component({
  selector: 'app-dashboard-metrics',
  standalone: true,
  template: `<div>Live Users: {{ activeUsers() }}</div>`
})
export class DashboardMetricsComponent {
  private metricsService = inject(MetricsService);

  // Modern Approach: toSignal handles automatic subscription & unsubscription
  activeUsers = toSignal(
    this.metricsService.userStream$.pipe(map(u => u.length)), 
    { initialValue: 0 }
  );
}""",
        "junior_eval": "Forgets to unsubscribe or manually creates a SubSink / ngOnDestroy unsubscribe array with heavy boilerplate.",
        "expert_eval": "Diagnoses GC retention through singleton observer closures, uses takeUntilDestroyed with explicit DestroyRef when outside constructor, or converts to Signals via toSignal()."
    })

    # Q4: Standalone Components & Module Migration
    questions.append({
        "id": 4,
        "badge": "Component Architecture & Bundling",
        "keywords": "standalone components ngmodule migration tree shaking providehttpclient lazy loading",
        "concept": "Standalone components (<code>standalone: true</code>), eliminating <code>NgModule</code> overhead, standalone route lazy loading (<code>loadComponent</code>), and modern standalone bootstrap.",
        "question": """An enterprise application migrates a legacy architecture containing 80 <code>NgModule</code> definitions to Angular 17/18 Standalone Components. Look at the code snippet.
<br><br>
<strong>Part A:</strong> What were the core architectural drawbacks of the traditional <code>NgModule</code> system regarding bundle size, mental model, and dead code tree-shaking?
<br>
<strong>Part B:</strong> How does lazy loading change with standalone components? Compare <code>loadChildren</code> pointing to a module vs <code>loadComponent: () => import(...)</code>.
<br>
<strong>Part C:</strong> How do you replace legacy module-level provider imports like <code>HttpClientModule</code> and <code>RouterModule.forRoot()</code> in a standalone <code>bootstrapApplication()</code> call?""",
        "snippet_title": "legacy-app.module.ts",
        "snippet_code": """@NgModule({
  declarations: [UserProfileComponent, UserBillingComponent],
  imports: [CommonModule, RouterModule, FormsModule, HttpClientModule],
  exports: [UserProfileComponent]
})
export class UserFeatureModule {}

const routes: Routes = [
  {
    path: 'users',
    loadChildren: () => import('./user-feature.module').then(m => m.UserFeatureModule)
  }
];""",
        "rating_concept": "Standalone components, standalone routing, provideHttpClient, and tree-shaking",
        "solution": """<strong>Part A (The Pitfalls of NgModule):</strong>
<br>• <strong>Tree-Shaking Barriers:</strong> In an NgModule, declaring 10 components forces the bundler to include all 10 in the module chunk, even if a route only renders one of them.
<br>• <strong>Context Indirection:</strong> Developers had to declare components in modules and import modules into other modules, creating complex dependency graphs where unused imports were never purged.
<br>• <strong>Mental Overhead:</strong> New developers struggled with the distinction between JavaScript ES modules (<code>import { x } from './x'</code>) and Angular <code>NgModule</code> metadata.
<br><br>
<strong>Part B (Fine-Grained Standalone Lazy Loading):</strong>
<br>• Standalone components declare their exact dependencies in their own <code>imports: [...]</code> array.
<br>• Routes use <code>loadComponent: () => import('./user-profile.component').then(c => c.UserProfileComponent)</code>.
<br>• Webpack / esbuild splits each individual standalone component into its own independent JavaScript chunk, downloading only what is rendered.
<br><br>
<strong>Part C (Standalone Bootstrap & Functional Providers):</strong>
<br>Modern Angular replaces modules with standalone provider functions:
<br>• <code>HttpClientModule</code> &rarr; <code>provideHttpClient(withInterceptors([...]))</code>
<br>• <code>RouterModule.forRoot(routes)</code> &rarr; <code>provideRouter(routes, withComponentInputBinding())</code>
<br>• <code>BrowserAnimationsModule</code> &rarr; <code>provideAnimationsAsync()</code>.""",
        "optimized_code": """// main.ts
bootstrapApplication(AppComponent, {
  providers: [
    provideRouter(appRoutes, withComponentInputBinding()),
    provideHttpClient(withInterceptors([authInterceptor])),
    provideAnimationsAsync()
  ]
});""",
        "junior_eval": "Wraps standalone components in dummy NgModules or imports entire CommonModule into every component instead of specific directives.",
        "expert_eval": "Articulates esbuild tree-shaking gains, converts routing to loadComponent chunks, and replaces module imports with functional providers (provideHttpClient, provideRouter)."
    })

    # Q5: Dependency Injection Hierarchy & Provider Scoping
    questions.append({
        "id": 5,
        "badge": "Dependency Injection & Scoping",
        "keywords": "dependency injection hierarchy providedin root element injector shadowing circular",
        "concept": "Angular Hierarchical Dependency Injection, Root vs Environment vs Element/Component Injectors, service instance shadowing, and <code>providedIn: 'root'</code> vs component <code>providers: []</code>.",
        "question": """A multi-page application shares a global <code>ShoppingCartService</code>. Look at the component code snippet.
<br><br>
<strong>Part A:</strong> In the navigation bar, the shopping cart shows 3 items. When the user opens the <code>CheckoutModalComponent</code>, the modal displays \"Cart is Empty!\" and items added inside the modal never appear in the navbar. Why did this state isolation bug happen?
<br>
<strong>Part B:</strong> Explain the multi-tier hierarchy of Angular Injectors (Platform Injector &rarr; Root Injector &rarr; Environment Injector &rarr; Element Injector).
<br>
<strong>Part C:</strong> When is placing a service inside a component's <code>providers: []</code> metadata intentionally desirable rather than an architectural bug?""",
        "snippet_title": "checkout-modal.component.ts",
        "snippet_code": """@Injectable({ providedIn: 'root' })
export class ShoppingCartService {
  items = signal<string[]>([]);
}

@Component({
  selector: 'app-checkout-modal',
  standalone: true,
  providers: [ShoppingCartService],
  template: `<div>Items in cart: {{ cart.items().length }}</div>`
})
export class CheckoutModalComponent {
  constructor(public cart: ShoppingCartService) {}
}""",
        "rating_concept": "Angular Hierarchical DI, Element Injectors, service shadowing, and provider scoping",
        "solution": """<strong>Part A (The Element Injector Shadowing Trap):</strong>
<br>• <code>ShoppingCartService</code> is configured with <code>providedIn: 'root'</code>, creating a single global singleton instance in the Root Injector.
<br>• However, <code>CheckoutModalComponent</code> specifies <code>providers: [ShoppingCartService]</code> on its <code>@Component</code> decorator.
<br>• This instructs Angular's <strong>Element Injector</strong> to instantiate a brand-new, isolated instance of <code>ShoppingCartService</code> scoped strictly to this modal component and its children.
<br>• The modal injects the newly created empty service, shadowing the root singleton. Any modifications inside the modal affect only the shadow instance!
<br><br>
<strong>Part B (The Injector Tree Hierarchy):</strong>
<br>1. <strong>Platform Injector:</strong> Singleton across multiple Angular applications on the same page (e.g. <code>DomSanitizer</code>).
<br>2. <strong>Root Injector:</strong> Application-level singletons (<code>providedIn: 'root'</code>).
<br>3. <strong>Environment Injector:</strong> Created by routed components or <code>createEnvironmentInjector()</code>.
<br>4. <strong>Element Injector:</strong> Created at each DOM component/directive level. Traversed upwards until a provider is found.
<br><br>
<strong>Part C (When Component-Level Providers are Desirable):</strong>
<br>Component-level providers are desired when state must be tied strictly to a component's lifecycle:
<br>• Reusable form controls or complex wizard steps that require clean, isolated state per widget instance.
<br>• Destroying the component automatically garbage-collects the service instance.""",
        "optimized_code": """@Component({
  selector: 'app-checkout-modal',
  standalone: true,
  // Fix: Remove providers: [ShoppingCartService] to share root singleton
  template: `<div>Items in cart: {{ cart.items().length }}</div>`
})
export class CheckoutModalComponent {
  cart = inject(ShoppingCartService); // Resolves to Root Singleton
}""",
        "junior_eval": "Blames Angular Signals or tries to pass the entire cart service instance via @Input() from parent to child.",
        "expert_eval": "Identifies Element Injector shadowing, diagrams the 4-tier injector tree, and distinguishes application singletons from lifecycle-bound widget providers."
    })

    # Q6: HTTP Interceptors: Functional vs Class-Based
    questions.append({
        "id": 6,
        "badge": "Network Architecture & Interceptors",
        "keywords": "http interceptor functional clone request 401 refresh token infinite loop",
        "concept": "Modern Functional HTTP Interceptors (<code>HttpInterceptorFn</code>), request immutability via <code>req.clone()</code>, refresh token replay mechanics, and preventing infinite 401 loops.",
        "question": """An application uses a functional HTTP interceptor to attach OAuth2 Bearer tokens and handle token refresh on 401 errors. Look at the code snippet.
<br><br>
<strong>Part A:</strong> Why is <code>HttpRequest</code> strictly immutable in Angular, requiring developers to call <code>req.clone()</code> to modify headers?
<br>
<strong>Part B:</strong> In the code snippet, if the refresh token endpoint itself (<code>/auth/refresh</code>) returns an <code>HTTP 401 Unauthorized</code>, the application enters an infinite recursive loop that freezes the browser. How do you prevent this?
<br>
<strong>Part C:</strong> How does modern Angular configure functional interceptors with <code>provideHttpClient(withInterceptors([...]))</code>, and how is dependency injection handled inside functional interceptors without a class constructor?""",
        "snippet_title": "auth.interceptor.ts",
        "snippet_code": """export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const token = authService.getToken();

  const cloned = req.clone({
    setHeaders: { Authorization: `Bearer ${token}` }
  });

  return next(cloned).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        return authService.refreshToken().pipe(
          switchMap(newToken => {
            return next(req.clone({
              setHeaders: { Authorization: `Bearer ${newToken}` }
            }));
          })
        );
      }
      return throwError(() => error);
    })
  );
};""",
        "rating_concept": "HttpInterceptorFn, request cloning immutability, and 401 refresh loop prevention",
        "solution": """<strong>Part A (HttpRequest Immutability):</strong>
<br>• HTTP requests are immutable because interceptors form a bidirectional pipeline.
<br>• If an interceptor or retry mechanism needs to resend a request, it requires the <strong>pristine original request</strong>.
<br>• Mutating the request object in-place would corrupt downstream retries, caching proxies, and cause race conditions across concurrent interceptor chains.
<br><br>
<strong>Part B (Preventing the 401 Infinite Loop):</strong>
<br>• If <code>authService.refreshToken()</code> invokes the backend <code>/api/auth/refresh</code> endpoint, that request <strong>also passes through this interceptor</strong>!
<br>• If the refresh token has expired, <code>/api/auth/refresh</code> returns 401, triggering another refresh call infinitely until the call stack or network crashes.
<br>• <strong>Fix:</strong> Check <code>req.url.includes('/auth/refresh')</code>. If the failing request is the refresh endpoint itself, bypass refresh logic, log out the user, and redirect to login.
<br><br>
<strong>Part C (Functional Interceptors & inject()):</strong>
<br>• <code>HttpInterceptorFn</code> runs inside an Angular injection context.
<br>• You call <code>inject(ServiceName)</code> directly at the function level without needing class constructors or <code>HTTP_INTERCEPTORS</code> multi-provider tokens.""",
        "optimized_code": """export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const router = inject(Router);

  // Exclude refresh endpoint from interceptor retry logic
  if (req.url.includes('/api/auth/refresh')) {
    return next(req);
  }

  const authReq = req.clone({ setHeaders: { Authorization: `Bearer ${auth.token()}` } });

  return next(authReq).pipe(
    catchError((err: HttpErrorResponse) => {
      if (err.status === 401) {
        return auth.refreshToken().pipe(
          switchMap(t => next(req.clone({ setHeaders: { Authorization: `Bearer ${t}` } }))),
          catchError(refreshErr => {
            auth.logout();
            router.navigate(['/login']);
            return throwError(() => refreshErr);
          })
        );
      }
      return throwError(() => err);
    })
  );
};""",
        "junior_eval": "Attempts to mutate req.headers directly without clone() or writes a token refresh interceptor that loops infinitely on expired refresh tokens.",
        "expert_eval": "Explains request immutability for retry safety, guards against recursive 401 refresh loops, and configures functional interceptors via inject() and provideHttpClient()."
    })

    # Q7: Advanced Form Architecture: Typed Forms & Async Validators
    questions.append({
        "id": 7,
        "badge": "Forms & Validation Architecture",
        "keywords": "typed forms reactive forms async validator debouncing switchmap valuechanges",
        "concept": "Typed Reactive Forms (Angular 14+), asynchronous validators (<code>AsyncValidatorFn</code>), avoiding backend request spamming via debouncing, and <code>updateOn: 'blur'</code>.",
        "question": """A user registration form validates username uniqueness against a backend database. Look at the component code snippet.
<br><br>
<strong>Part A:</strong> As the user types \"alexander\", the async validator sends 9 consecutive HTTP requests to the backend for every keystroke. Explain how this keystroke spamming degrades backend database performance and how to fix it using RxJS <code>timer()</code> and <code>switchMap()</code>.
<br>
<strong>Part B:</strong> What is the difference between setting <code>updateOn: 'change'</code> (default) versus <code>updateOn: 'blur'</code> on form controls?
<br>
<strong>Part C:</strong> How do <strong>Typed Reactive Forms</strong> prevent runtime bugs compared to legacy untyped forms? What happens if you try to call <code>form.controls.nonExistentField</code> in TypeScript?""",
        "snippet_title": "registration-form.component.ts",
        "snippet_code": """export function usernameValidator(userService: UserService): AsyncValidatorFn {
  return (control: AbstractControl): Observable<ValidationErrors | null> => {
    return userService.checkUsername(control.value).pipe(
      map(isTaken => isTaken ? { usernameTaken: true } : null),
      catchError(() => of(null))
    );
  };
}

@Component({
  selector: 'app-registration',
  standalone: true,
  imports: [ReactiveFormsModule],
  template: `<input [formControl]="form.controls.username">`
})
export class RegistrationComponent {
  form = new FormGroup({
    username: new FormControl('', {
      asyncValidators: [usernameValidator(inject(UserService))]
    })
  });
}""",
        "rating_concept": "Typed Reactive Forms, async validator debouncing, and updateOn blur tuning",
        "solution": """<strong>Part A (Debouncing Async Validators with timer):</strong>
<br>• By default, <code>asyncValidators</code> execute on every single keystroke event.
<br>• Typing rapidly fires multiple pending asynchronous HTTP requests. If network responses arrive out of order, stale responses can overwrite fresh validation states!
<br>• <strong>Fix:</strong> Wrap the check in <code>timer(300)</code> followed by <code>switchMap()</code>. If the user types another character within 300ms, the timer is cancelled and prior pending HTTP requests are aborted.
<br><br>
<strong>Part B (updateOn: 'change' vs 'blur'):</strong>
<br>• <code>updateOn: 'change'</code> (default): Emits values and runs validators on every character typed.
<br>• <code>updateOn: 'blur'</code>: Runs validation only when the user tabs or clicks away from the input field. For heavy async database validations, setting <code>updateOn: 'blur'</code> slashes server validation requests by 90%.
<br><br>
<strong>Part C (Typed Reactive Forms Benefits):</strong>
<br>• Since Angular 14, <code>FormGroup</code> and <code>FormControl</code> are strictly typed.
<br>• <code>form.controls.nonExistentField</code> triggers a <strong>compile-time TypeScript error</strong> (<code>Property does not exist on type...</code>).
<br>• <code>form.value</code> produces a strongly typed interface (e.g. <code>{ username: string | null }</code>), eliminating runtime <code>undefined</code> bugs.""",
        "optimized_code": """export function debouncedUsernameValidator(userService: UserService): AsyncValidatorFn {
  return (control: AbstractControl): Observable<ValidationErrors | null> => {
    if (!control.value) return of(null);
    return timer(300).pipe(
      switchMap(() => userService.checkUsername(control.value)),
      map(taken => taken ? { usernameTaken: true } : null),
      catchError(() => of(null))
    );
  };
}

// Or configure updateOn: 'blur'
username = new FormControl('', {
  updateOn: 'blur',
  asyncValidators: [debouncedUsernameValidator(inject(UserService))]
});""",
        "junior_eval": "Leaves async validators un-debounced or handles debouncing manually inside template (input) event listeners.",
        "expert_eval": "Implements timer/switchMap debouncing inside the AsyncValidatorFn, tunes updateOn to 'blur' for expensive network validations, and leverages Typed Forms for compile-time safety."
    })

    # Q8: Route Guards & Lazy Loading: CanActivate vs CanMatch
    questions.append({
        "id": 8,
        "badge": "Routing & Security Guards",
        "keywords": "route guards canactivate canmatch candeactivate lazy loading security bundle leak",
        "concept": "Functional Route Guards (<code>CanActivateFn</code>, <code>CanMatchFn</code>, <code>CanDeactivateFn</code>), preventing unauthorized bundle downloads via <code>CanMatch</code>, and unsaved changes confirmation.",
        "question": """An enterprise portal contains an Admin Console containing sensitive business logic. Look at the routing configuration snippet.
<br><br>
<strong>Part A:</strong> A standard non-admin user navigates to <code>/admin</code>. The <code>canActivate</code> guard successfully blocks access and redirects to <code>/forbidden</code>. However, the browser Network tab reveals that the 5 MB <code>admin-console.js</code> chunk was already downloaded to the user's browser! Why does <code>canActivate</code> download the bundle, and how does <strong><code>canMatch</code></strong> fix this security leak?
<br>
<strong>Part B:</strong> How do you implement a <code>CanDeactivateFn</code> guard to prevent users from accidentally navigating away from a form with unsaved changes?
<br>
<strong>Part C:</strong> Contrast a Route Resolver (<code>ResolveFn</code>) against fetching data inside component <code>ngOnInit()</code>. What happens to the router transition if a resolver observable never completes?""",
        "snippet_title": "app.routes.ts",
        "snippet_code": """export const routes: Routes = [
  {
    path: 'admin',
    canActivate: [() => inject(AuthService).isAdmin()],
    loadComponent: () => import('./admin/admin-console.component')
      .then(m => m.AdminConsoleComponent)
  }
];""",
        "rating_concept": "CanMatch vs CanActivate bundle security, CanDeactivate guards, and Route Resolvers",
        "solution": """<strong>Part A (The CanActivate Bundle Download Vulnerability):</strong>
<br>• <code>canActivate</code> runs <strong>after</strong> the router has matched the route and downloaded the lazy code chunk!
<br>• The browser downloads the entire 5 MB admin bundle before the guard evaluates. A malicious user can inspect source maps or minified JavaScript to find hidden API endpoints, algorithms, and admin secrets.
<br>• <strong>CanMatch Defense:</strong> <code>canMatch</code> evaluates <strong>before</strong> the route is matched. If it returns false, the router does not match the route and <strong>never downloads the lazy JavaScript chunk</strong> over the network.
<br><br>
<strong>Part B (CanDeactivate Implementation):</strong>
<br>• <code>CanDeactivateFn&lt;T&gt;</code> receives the active component instance.
<br>• It checks <code>component.hasUnsavedChanges()</code>. If true, it presents a confirmation modal and returns a <code>Promise&lt;boolean&gt;</code> or <code>Observable&lt;boolean&gt;</code> based on user decision.
<br><br>
<strong>Part C (Route Resolvers & Stalled Navigation):</strong>
<br>• <code>ResolveFn</code> pre-fetches data before rendering the component, preventing layout pop-in.
<br>• However, the router navigation <strong>remains blocked in limbo</strong> until the resolver observable completes. If the backend hangs or the observable does not emit completion (like an uncompleted Subject), the user is stuck on the previous page with no feedback.""",
        "optimized_code": """export const routes: Routes = [
  {
    path: 'admin',
    // canMatch prevents the JS bundle chunk from ever being downloaded
    canMatch: [() => inject(AuthService).isAdmin()],
    loadComponent: () => import('./admin/admin-console.component')
      .then(m => m.AdminConsoleComponent)
  }
];""",
        "junior_eval": "Uses canActivate for all routes, unaware that proprietary admin JavaScript chunks are leaked to unauthorized clients.",
        "expert_eval": "Enforces canMatch to prevent unauthorized bundle downloading, implements CanDeactivate for dirty forms, and handles error timeouts on Route Resolvers."
    })

    # Q9: Content Projection & Dynamic Component Creation
    questions.append({
        "id": 9,
        "badge": "Component Composition & DOM Manipulation",
        "keywords": "content projection ng-content viewcontainerref ng-template createcomponent lifecycle",
        "concept": "Content Projection (<code>ng-content</code>), projected component lifecycle execution traps, template instantiation via <code>ng-template</code>, and dynamic component rendering via <code>ViewContainerRef</code>.",
        "question": """A reusable modal dialog component uses multi-slot content projection. Look at the template snippet.
<br><br>
<strong>Part A:</strong> Look at <code>*ngIf="isOpen"</code> placed on <code>&lt;ng-content&gt;</code>. Even when the modal is closed (<code>isOpen = false</code>), the heavy chart inside <code>&lt;app-heavy-chart&gt;</code> executes its <code>ngOnInit()</code> and fetches data from the backend. Why does <code>*ngIf</code> fail on <code>&lt;ng-content&gt;</code>?
<br>
<strong>Part B:</strong> How does wrapping the projected content in <code>&lt;ng-template&gt;</code> solve this lifecycle issue by deferring component instantiation until the modal actually opens?
<br>
<strong>Part C:</strong> How do you dynamically instantiate a component at runtime using <code>ViewContainerRef.createComponent()</code>, and how do you pass inputs to it using modern <code>ComponentRef.setInput()</code>?""",
        "snippet_title": "modal-dialog.component.html",
        "snippet_code": """<!-- modal-dialog.component.html -->
<div class="modal" *ngIf="isOpen">
  <div class="modal-body">
    <!-- Problem: *ngIf does not stop projected content from instantiating! -->
    <ng-content *ngIf="isOpen" select="[modal-body]"></ng-content>
  </div>
</div>

<!-- Usage in parent -->
<app-modal-dialog [isOpen]="showModal">
  <app-heavy-chart modal-body></app-heavy-chart>
</app-modal-dialog>""",
        "rating_concept": "Content projection ng-content lifecycle traps, ng-template deferred rendering, and ViewContainerRef",
        "solution": """<strong>Part A (The ng-content Lifecycle Trap):</strong>
<br>• <code>&lt;ng-content&gt;</code> does <strong>not produce real DOM</strong>; it is simply a placeholder marker indicating where projected nodes should be moved.
<br>• The projected component (<code>&lt;app-heavy-chart&gt;</code>) is declared in the <strong>parent component's template</strong>.
<br>• Therefore, the parent component instantiates <code>&lt;app-heavy-chart&gt;</code> immediately during parent rendering!
<br>• Placing <code>*ngIf</code> on <code>&lt;ng-content&gt;</code> only hides or shows the projected DOM nodes after they have already been constructed and initialized. Its <code>ngOnInit()</code> has already executed!
<br><br>
<strong>Part B (Deferred Instantiation with ng-template):</strong>
<br>• <code>&lt;ng-template&gt;</code> tells Angular: <em>\"Do not instantiate this component now; compile it as a blueprint.\"</em>
<br>• The modal receives a <code>TemplateRef</code> and renders it using <code>&lt;ng-container *ngTemplateOutlet="tpl"&gt;</code> only when <code>isOpen = true</code>.
<br>• <code>ngOnInit()</code> executes only when the modal opens, saving memory and network calls.
<br><br>
<strong>Part C (Dynamic Creation via ViewContainerRef):</strong>
<br>Inject <code>ViewContainerRef</code> and call <code>vcr.createComponent(DynamicComponent)</code>. In modern Angular, pass inputs using <code>compRef.setInput('propName', value)</code> to trigger OnPush change detection properly.""",
        "optimized_code": """<!-- Parent Template uses ng-template for lazy instantiation -->
<app-modal-dialog [isOpen]="showModal">
  <ng-template modal-body>
    <app-heavy-chart></app-heavy-chart>
  </ng-template>
</app-modal-dialog>

<!-- Modal Component Template -->
<div class="modal" *ngIf="isOpen">
  <ng-container *ngTemplateOutlet="bodyTemplate"></ng-container>
</div>""",
        "junior_eval": "Places *ngIf directly on <ng-content> and cannot explain why child component network requests fire on initial page load.",
        "expert_eval": "Articulates that projected nodes are owned and initialized by the host/parent, replaces ng-content with ng-template for deferred instantiation, and uses ViewContainerRef.createComponent()."
    })

    # Q10: State Management: NgRx Store vs SignalStore
    questions.append({
        "id": 10,
        "badge": "State Management Architecture",
        "keywords": "ngrx store signalstore redux effects immutability state normalization",
        "concept": "Global Redux state management (NgRx Store, Reducers, Effects) versus modern <code>@ngrx/signals</code> (SignalStore), state normalization, and Effect error resilience.",
        "question": """An enterprise financial portal architect evaluates state management patterns for a large development team. Look at the NgRx Effect code snippet.
<br><br>
<strong>Part A:</strong> In the NgRx Effect, if an HTTP call returns <code>HTTP 500</code>, the error is caught at the root level of the effect. Why does this <strong>permanently terminate the Effect stream</strong>, causing all subsequent user button clicks to be ignored?
<br>
<strong>Part B:</strong> How does modern <strong>NgRx SignalStore</strong> (<code>signalStore()</code> with <code>withState</code>, <code>withComputed</code>, <code>withMethods</code>) eliminate Redux boilerplate (actions, reducers, selectors) while maintaining type safety?
<br>
<strong>Part C:</strong> What is <strong>State Normalization</strong>, and why should nested relational data (e.g. Users with Orders with Items) be normalized by ID in client-side state?""",
        "snippet_title": "order.effects.ts",
        "snippet_code": """@Injectable()
export class OrderEffects {
  loadOrders$ = createEffect(() =>
    this.actions$.pipe(
      ofType(OrderActions.loadOrders),
      switchMap(() => this.orderService.fetchOrders()),
      map(orders => OrderActions.loadOrdersSuccess({ orders })),
      // Critical Bug: Catching error on the main effect stream!
      catchError(error => of(OrderActions.loadOrdersFailure({ error })))
    )
  );

  constructor(private actions$: Actions, private orderService: OrderService) {}
}""",
        "rating_concept": "NgRx Effects stream termination, SignalStore architecture, and state normalization",
        "solution": """<strong>Part A (The Terminated Effect Stream Disaster):</strong>
<br>• In RxJS, when an error reaches a stream's <code>catchError()</code> operator, it emits the fallback value and <strong>completes the stream</strong>.
<br>• Because <code>catchError</code> is placed on the outer <code>actions$</code> stream, the entire <code>loadOrders$</code> Effect completes permanently on the first HTTP failure!
<br>• The Effect stops listening for <code>OrderActions.loadOrders</code> actions. Subsequent user clicks dispatch actions into the void.
<br><strong>Fix:</strong> Move <code>catchError</code> inside the inner <code>switchMap()</code> pipe so only the inner HTTP observable completes on error.
<br><br>
<strong>Part B (NgRx SignalStore Advantages):</strong>
<br>• Native Angular Signals integration (zero Zone.js overhead).
<br>• No separate Actions, Reducers, Selectors, or Dispatchers needed.
<br>• Composable building blocks: <code>withState()</code>, <code>withComputed()</code>, <code>withMethods()</code>.
<br><br>
<strong>Part C (State Normalization):</strong>
<br>Storing entities in relational dictionary format (<code>entities: { [id: string]: Order }, ids: string[]</code>) prevents duplicate data anomalies. Updating an order updates one single dictionary entry without traversing deep arrays.""",
        "optimized_code": """// Fix: catchError must be INSIDE switchMap
loadOrders$ = createEffect(() =>
  this.actions$.pipe(
    ofType(OrderActions.loadOrders),
    switchMap(() =>
      this.orderService.fetchOrders().pipe(
        map(orders => OrderActions.loadOrdersSuccess({ orders })),
        catchError(error => of(OrderActions.loadOrdersFailure({ error })))
      )
    )
  )
);""",
        "junior_eval": "Catches errors on the outer Effect stream (killing the listener) or insists on writing full global Redux boilerplate for a simple component toggle.",
        "expert_eval": "Diagnoses outer stream completion bugs in RxJS Effects, structures inner flattening operators, and advocates for SignalStore for type-safe, lightweight state management."
    })

    # Q11: Zone.js Internals & Zoneless Angular
    questions.append({
        "id": 11,
        "badge": "Runtime Internals & Zoneless",
        "keywords": "zonejs monkey patch runoutsideangular zoneless angular 18 microtask macrotask",
        "concept": "How Zone.js monkey-patches browser asynchronous APIs, <code>ngZone.runOutsideAngular()</code>, execution frame drops, and Zoneless Angular (Angular 18+).",
        "question": """A high-frequency charting dashboard plots real-time financial trades on a Canvas element. Look at the component code snippet.
<br><br>
<strong>Part A:</strong> The canvas animation triggers severe UI lag, frame rate drops from 60 FPS to 12 FPS, and high CPU usage. Explain how Zone.js monkey-patching <code>requestAnimationFrame</code> or mouse events causes this performance collapse.
<br>
<strong>Part B:</strong> How do you use <code>NgZone.runOutsideAngular()</code> to execute high-frequency loops without triggering Angular change detection?
<br>
<strong>Part C:</strong> How does <strong>Zoneless Angular (Angular 18+)</strong> work via <code>provideExperimentalZonelessChangeDetection()</code>? What replaces Zone.js to notify Angular when templates need re-rendering?""",
        "snippet_title": "trading-chart.component.ts",
        "snippet_code": """@Component({
  selector: 'app-trading-chart',
  standalone: true,
  template: `<canvas #chartCanvas (mousemove)="onMouseMove($event)"></canvas>`
})
export class TradingChartComponent implements AfterViewInit {
  @ViewChild('chartCanvas') canvasRef!: ElementRef<HTMLCanvasElement>;

  ngAfterViewInit() {
    this.startRenderingLoop();
  }

  startRenderingLoop() {
    const render = () => {
      this.drawCanvasFrame();
      requestAnimationFrame(render);
    };
    requestAnimationFrame(render);
  }

  onMouseMove(e: MouseEvent) {
    this.updateCrosshair(e.clientX, e.clientY);
  }

  private drawCanvasFrame() {}
  private updateCrosshair(x: number, y: number) {}
}""",
        "rating_concept": "Zone.js monkey-patching, runOutsideAngular, and Zoneless Angular 18",
        "solution": """<strong>Part A (Zone.js Monkey-Patching Overhead):</strong>
<br>• Zone.js intercepts all asynchronous browser APIs: <code>addEventListener</code>, <code>requestAnimationFrame</code>, <code>setTimeout</code>, and <code>fetch</code>.
<br>• Running <code>requestAnimationFrame</code> (60 times/sec) or <code>mousemove</code> inside the Angular zone causes Zone.js to emit an <code>onMicrotaskEmpty</code> event on <strong>every single frame</strong>!
<br>• Angular runs change detection across the entire component tree 60+ times per second, recalculating bindings and destroying rendering performance.
<br><br>
<strong>Part B (runOutsideAngular Solution):</strong>
<br>Inject <code>NgZone</code> and execute the loop and listeners inside <code>this.ngZone.runOutsideAngular(() => ...)</code>.
<br>Zone.js will ignore the events, allowing the canvas to render at a buttery 60 FPS without triggering Angular change detection passes.
<br><br>
<strong>Part C (Zoneless Angular in v18+):</strong>
<br>• Zoneless completely eliminates the Zone.js monkey-patching runtime library (reducing bundle size by ~15KB).
<br>• Instead of relying on intercepted async browser events, Angular relies on <strong>explicit scheduler notifications</strong>:
<br>1. Signal updates (<code>signal.set()</code>).
<br>2. <code>ChangeDetectorRef.markForCheck()</code>.
<br>3. Template event listeners (e.g. <code>(click)</code>).
<br>4. <code>AsyncPipe</code> emissions.""",
        "optimized_code": """ngAfterViewInit() {
  this.ngZone.runOutsideAngular(() => {
    const canvas = this.canvasRef.nativeElement;
    canvas.addEventListener('mousemove', e => this.updateCrosshair(e.clientX, e.clientY));
    
    const render = () => {
      this.drawCanvasFrame();
      requestAnimationFrame(render);
    };
    requestAnimationFrame(render);
  });
}""",
        "junior_eval": "Blames the HTML5 Canvas API or browser performance without understanding Zone.js change detection triggers.",
        "expert_eval": "Explains Zone.js async API monkey-patching, isolates high-frequency loops using runOutsideAngular(), and outlines Zoneless Angular 18 scheduler mechanics."
    })

    # Q12: Custom Structural Directives & TemplateRef
    questions.append({
        "id": 12,
        "badge": "Directive Architecture & DOM Mechanics",
        "keywords": "structural directive templateRef viewcontainerref asterisk micro syntax microsyntax",
        "concept": "Custom structural directives, the asterisk (<code>*</code>) template micro-syntax desugaring, <code>TemplateRef</code> and <code>ViewContainerRef</code>, and type-safe template context.",
        "question": """A security team creates a role-based structural directive: <code>*appHasRole=\"['ADMIN', 'MANAGER']\"</code>. Look at the directive implementation.
<br><br>
<strong>Part A:</strong> How does the Angular compiler internally desugar the asterisk micro-syntax (<code>*appHasRole=\"roles\"</code>) into an explicit HTML element?
<br>
<strong>Part B:</strong> In the code snippet, if the user's roles change dynamically from User to Admin, multiple duplicate views are inserted into the DOM. Explain why.
<br>
<strong>Part C:</strong> How do you use the static <code>ngTemplateContextGuard</code> method to provide strongly typed IntelliSense for template variables (e.g. <code>*appHasRole=\"['ADMIN']; let permission = permission\"</code>)?""",
        "snippet_title": "has-role.directive.ts",
        "snippet_code": """@Directive({
  selector: '[appHasRole]',
  standalone: true
})
export class HasRoleDirective {
  @Input() set appHasRole(requiredRoles: string[]) {
    const userRoles = this.authService.getUserRoles();
    const hasPermission = requiredRoles.some(r => userRoles.includes(r));

    if (hasPermission) {
      // Bug: Repeatedly inserts duplicate views without clearing previous views
      this.vcr.createEmbeddedView(this.templateRef);
    } else {
      this.vcr.clear();
    }
  }

  constructor(
    private templateRef: TemplateRef<any>,
    private vcr: ViewContainerRef,
    private authService: AuthService
  ) {}
}""",
        "rating_concept": "Structural directives, asterisk desugaring, and ViewContainerRef embedded views",
        "solution": """<strong>Part A (The Asterisk Micro-Syntax Desugaring):</strong>
<br>When Angular compiles <code>&lt;div *appHasRole=\"['ADMIN']\"&gt;Secret Content&lt;/div&gt;</code>, it desugars the template into:
<br><code>&lt;ng-template [appHasRole]=\"['ADMIN']\"&gt;&lt;div&gt;Secret Content&lt;/div&gt;&lt;/ng-template&gt;</code>
<br>The directive is attached to the <code>&lt;ng-template&gt;</code> element and receives <code>TemplateRef</code> and <code>ViewContainerRef</code> via dependency injection.
<br><br>
<strong>Part B (The Duplicate View Leak):</strong>
<br>• Every time the <code>@Input()</code> setter fires, if <code>hasPermission</code> is true, it calls <code>this.vcr.createEmbeddedView()</code>.
<br>• <code>createEmbeddedView</code> <strong>appends</strong> a new view instance to the container.
<br>• If the setter fires multiple times while the user remains authorized, duplicate DOM trees are inserted repeatedly.
<br>• <strong>Fix:</strong> Maintain a boolean flag <code>hasView</code>. Only call <code>createEmbeddedView()</code> if <code>!this.hasView</code>, and call <code>vcr.clear()</code> when revoking permission.
<br><br>
<strong>Part C (Type-Safe Context with ngTemplateContextGuard):</strong>
<br>Declare a typed Context interface (<code>HasRoleContext</code>) and a static type-guard:
<br><code>static ngTemplateContextGuard(dir: HasRoleDirective, ctx: any): ctx is HasRoleContext { return true; }</code>
<br>This provides full TypeScript compiler type-checking inside the template.""",
        "optimized_code": """private hasView = false;

@Input() set appHasRole(requiredRoles: string[]) {
  const hasPermission = requiredRoles.some(r => this.authService.getUserRoles().includes(r));

  if (hasPermission && !this.hasView) {
    this.vcr.createEmbeddedView(this.templateRef);
    this.hasView = true;
  } else if (!hasPermission && this.hasView) {
    this.vcr.clear();
    this.hasView = false;
  }
}""",
        "junior_eval": "Confuses structural directives with attribute directives or cannot explain how the asterisk (*) transforms into an ng-template.",
        "expert_eval": "Explains template micro-syntax compilation, manages ViewContainerRef view lifecycles to prevent duplicate DOM insertion, and uses ngTemplateContextGuard for typed templates."
    })

    # Q13: SSR Hydration & Server-Side Rendering
    questions.append({
        "id": 13,
        "badge": "SSR, Hydration & Universal",
        "keywords": "ssr hydration non destructive server side rendering window localstorage isplatformbrowser",
        "concept": "Server-Side Rendering (SSR with <code>@angular/ssr</code>), Non-Destructive Hydration, avoiding direct DOM/browser API access (<code>isPlatformBrowser</code>), and <code>afterRender</code> lifecycle hooks.",
        "question": """An Angular 17 application enables Server-Side Rendering (SSR) and non-destructive hydration. Look at the component code snippet.
<br><br>
<strong>Part A:</strong> During server-side pre-rendering on Node.js, the server crashes with <code>ReferenceError: window is not defined</code> or <code>localStorage is not defined</code>. Why do standard browser globals fail in SSR?
<br>
<strong>Part B:</strong> What is <strong>Non-Destructive Hydration</strong> in modern Angular, and how does it prevent the visual \"flickering\" that plagued legacy Angular Universal?
<br>
<strong>Part C:</strong> What is the difference between <code>afterRender()</code> / <code>afterNextRender()</code> and traditional lifecycle hooks like <code>ngOnInit()</code> during SSR?""",
        "snippet_title": "user-theme.component.ts",
        "snippet_code": """@Component({
  selector: 'app-user-theme',
  standalone: true,
  template: `<div>Current Theme: {{ theme }}</div>`
})
export class UserThemeComponent implements OnInit {
  theme = 'light';

  ngOnInit() {
    // Problem: Crashes on Server-Side Rendering (Node.js)
    const saved = window.localStorage.getItem('theme');
    if (saved) {
      this.theme = saved;
    }
  }
}""",
        "rating_concept": "SSR Non-Destructive Hydration, isPlatformBrowser, and afterNextRender lifecycle",
        "solution": """<strong>Part A (Browser Globals in Node.js Runtime):</strong>
<br>• During SSR, Angular executes on a Node.js server to render static HTML.
<br>• Node.js has no browser global objects: <code>window</code>, <code>document</code>, <code>localStorage</code>, <code>sessionStorage</code>, and <code>navigator</code> do not exist.
<br>• Referencing <code>window.localStorage</code> throws an unhandled <code>ReferenceError</code> that terminates the server process.
<br>• <strong>Fix:</strong> Guard browser-only logic with <code>isPlatformBrowser(inject(PLATFORM_ID))</code>.
<br><br>
<strong>Part B (Non-Destructive Hydration):</strong>
<br>• <strong>Legacy Destructive SSR:</strong> Rendered HTML on the server. When the client bundle loaded, Angular wiped out the entire server-rendered DOM and recreated every single DOM node from scratch, causing an ugly visual flash/flicker.
<br>• <strong>Non-Destructive Hydration:</strong> Angular scans the existing server-rendered DOM, matches components to DOM nodes, and attaches event listeners in-place without destroying or recreating elements.
<br><br>
<strong>Part C (afterRender & afterNextRender Lifecycle):</strong>
<br>• <code>afterRender</code> and <code>afterNextRender</code> execute <strong>only in the browser</strong>, never on the server.
<br>• They are the recommended Angular 17+ hooks for DOM measurements, canvas drawing, and accessing third-party browser libraries without needing platform checks.""",
        "optimized_code": """export class UserThemeComponent {
  theme = 'light';

  constructor() {
    // afterNextRender runs ONLY on the browser, never on the SSR server
    afterNextRender(() => {
      const saved = localStorage.getItem('theme');
      if (saved) this.theme = saved;
    });
  }
}""",
        "junior_eval": "Uses window directly or wraps code in try-catch without understanding that SSR runs in a headless Node.js environment.",
        "expert_eval": "Guards against Node.js runtime crashes, explains Non-Destructive DOM Hydration node attachment, and leverages afterNextRender() for browser-only DOM operations."
    })

    # Q14: Control Flow Syntax (@if, @for, @switch)
    questions.append({
        "id": 14,
        "badge": "Compiler & Template Architecture",
        "keywords": "control flow syntax if for switch track trackby performance commonmodule dom thrashing",
        "concept": "Modern built-in control flow syntax (<code>@if</code>, <code>@for ... track</code>, <code>@switch</code>), eliminating <code>CommonModule</code> imports, and preventing DOM thrashing via mandatory tracking.",
        "question": """A real-time financial order book renders 2,000 live trades. Look at the template snippet comparing legacy vs modern control flow.
<br><br>
<strong>Part A:</strong> In the legacy <code>*ngFor</code> template without <code>trackBy</code>, every time the trades array is updated, all 2,000 DOM table rows are destroyed and recreated, causing massive browser lag. Why does missing <code>trackBy</code> cause DOM thrashing?
<br>
<strong>Part B:</strong> How does the new built-in control flow syntax (<code>@for (trade of trades; track trade.id)</code>) make tracking mandatory, and how does the Angular compiler optimize it?
<br>
<strong>Part C:</strong> Why does the new control flow syntax eliminate the need to import <code>CommonModule</code> (or <code>NgIf</code>/<code>NgFor</code>) into Standalone Components?""",
        "snippet_title": "order-book.component.html",
        "snippet_code": """<!-- Legacy Approach (CommonModule required) -->
<tr *ngFor="let trade of trades">
  <td>{{ trade.id }}</td>
  <td>{{ trade.price }}</td>
</tr>

<!-- Modern Control Flow Syntax (Angular 17+) -->
@for (trade of trades; track trade.id) {
  <tr>
    <td>{{ trade.id }}</td>
    <td>{{ trade.price }}</td>
  </tr>
} @empty {
  <tr><td colspan="2">No active trades</td></tr>
}""",
        "rating_concept": "Control flow syntax (@if/@for), mandatory track expressions, and DOM thrashing prevention",
        "solution": """<strong>Part A (DOM Thrashing without trackBy):</strong>
<br>• Without a tracking identifier, <code>*ngFor</code> tracks items strictly by <strong>object identity (reference)</strong>.
<br>• When a fresh array is received from an API or immutable store, even if the trade IDs and data are identical, the object references in memory are new.
<br>• Angular assumes all previous items were deleted and 2,000 new items were added. It tears down all 2,000 DOM nodes and inserts 2,000 fresh DOM nodes, running expensive layout, styling, and paint recalculations.
<br><br>
<strong>Part B (Mandatory track Expression in @for):</strong>
<br>• Angular 17+ makes <code>track</code> a <strong>mandatory compile-time requirement</strong> in <code>@for</code>.
<br>• The compiler enforces tracking by unique ID (e.g. <code>track trade.id</code>).
<br>• When an updated array arrives, Angular matches existing DOM nodes by ID, reusing DOM elements and updating only the mutated text bindings with sub-millisecond efficiency.
<br><br>
<strong>Part C (Compiler-Level Primitives vs Directives):</strong>
<br>• <code>*ngIf</code> and <code>*ngFor</code> were structural directives that required importing JavaScript classes from <code>@angular/common</code>.
<br>• <code>@if</code>, <code>@for</code>, and <code>@switch</code> are built directly into the Angular template compiler grammar, requiring zero module imports and producing smaller, faster compiled JavaScript code.""",
        "optimized_code": """@for (trade of trades(); track trade.id) {
  <tr>
    <td>{{ trade.id }}</td>
    <td>{{ trade.price | currency }}</td>
  </tr>
} @empty {
  <tr><td colspan="2">No active trades recorded.</td></tr>
}""",
        "junior_eval": "Omits trackBy in *ngFor or thinks @for is merely syntactic sugar that works identically to *ngFor under the hood.",
        "expert_eval": "Explains DOM thrashing and layout thrashing without tracking, details compiler-level AST transformation of @for, and leverages @empty blocks."
    })

    # Q15: Deferrable Views (@defer)
    questions.append({
        "id": 15,
        "badge": "Performance Optimization & Code Splitting",
        "keywords": "deferrable views defer placeholder loading error on viewport on interaction prefetch",
        "concept": "Deferrable Views (<code>@defer</code>), template-level automated code-splitting, trigger conditions (<code>on viewport</code>, <code>on interaction</code>, <code>on idle</code>), and prefetching.",
        "question": """A heavy analytics dashboard embeds a complex D3 chart library (3 MB) at the bottom of the page below the fold. Look at the template snippet.
<br><br>
<strong>Part A:</strong> How does <strong><code>@defer</code></strong> automate code-splitting at the component template level without requiring complex route splitting or manual dynamic imports?
<br>
<strong>Part B:</strong> Explain the distinct roles of the four blocks: <code>@defer</code>, <code>@placeholder</code>, <code>@loading</code>, and <code>@error</code>.
<br>
<strong>Part C:</strong> Contrast trigger conditions: <code>on viewport</code>, <code>on interaction</code>, and <code>on idle</code>. How does combining <code>@defer (on interaction; prefetch on idle)</code> optimize user experience?""",
        "snippet_title": "analytics-page.component.html",
        "snippet_code": """<div class="summary-section">
  <h1>Executive Summary</h1>
</div>

<!-- Deferrable View below the fold -->
@defer (on viewport; prefetch on idle) {
  <app-heavy-d3-chart [data]="chartData"></app-heavy-d3-chart>
} @placeholder (minimum 500ms) {
  <div class="chart-skeleton">Scroll down to view chart...</div>
} @loading (after 100ms; minimum 500ms) {
  <div class="spinner">Loading chart analytics engine...</div>
} @error {
  <div class="alert">Failed to load chart bundle.</div>
}""",
        "rating_concept": "Deferrable views (@defer), viewport triggers, prefetching, and template code-splitting",
        "solution": """<strong>Part A (Template-Level Code-Splitting):</strong>
<br>• Any components, directives, and third-party libraries used exclusively inside a <code>@defer</code> block are <strong>automatically bundled into a separate lazy JavaScript chunk</strong> by esbuild/Webpack.
<br>• The main initial bundle downloads in milliseconds because the 3 MB D3 library is stripped out entirely.
<br><br>
<strong>Part B (The 4 Defer Blocks):</strong>
<br>• <code>@defer</code>: The main content to be lazily loaded and rendered once conditions are satisfied.
<br>• <code>@placeholder</code>: Rendered initially before loading begins. (Supports <code>minimum</code> display duration to prevent flickering).
<br>• <code>@loading</code>: Displayed while the deferred JavaScript chunk is actively being fetched across the network.
<br>• <code>@error</code>: Fallback UI displayed if chunk downloading fails (e.g. network disconnection).
<br><br>
<strong>Part C (Triggers & Prefetching):</strong>
<br>• <code>on viewport</code>: Triggers when the placeholder enters the browser visible viewport (via IntersectionObserver).
<br>• <code>on interaction</code>: Triggers when the user clicks or focuses on the placeholder.
<br>• <code>on idle</code>: Triggers when the browser has finished all critical tasks and enters an idle state (via <code>requestIdleCallback</code>).
<br>• <code>@defer (on interaction; prefetch on idle)</code>: Downloads the heavy chunk in the background while the browser is idle, so when the user actually clicks, it renders <strong>instantaneously with zero loading lag</strong>!""",
        "optimized_code": """@defer (on viewport; prefetch on idle) {
  <app-heavy-d3-chart [data]="chartData()"></app-heavy-d3-chart>
} @placeholder {
  <div class="skeleton-chart">Loading preview...</div>
}""",
        "junior_eval": "Bundles all heavy third-party visualization libraries into the main bundle or attempts manual dynamic imports with ngComponentOutlet.",
        "expert_eval": "Leverages @defer for template-level code splitting, uses IntersectionObserver viewport triggers, and pairs prefetch on idle with interaction triggers to eliminate UI delay."
    })

    # Q16: Angular Security: XSS & DomSanitizer
    questions.append({
        "id": 16,
        "badge": "Frontend Security & XSS Mitigation",
        "keywords": "domsanitizer xss security contexts bypasssecuritytrusthtml dompurify innerhtml",
        "concept": "Angular built-in Cross-Site Scripting (XSS) prevention, context-aware escaping (HTML, Style, URL, ResourceURL), <code>DomSanitizer</code> security risks, and safe HTML sanitization via DOMPurify.",
        "question": """A content management system allows administrators to post formatted customer notices. Look at the component code snippet.
<br><br>
<strong>Part A:</strong> An administrator pastes content containing <code>&lt;img src=\"x\" onerror=\"stealTokens()\"&gt;</code>. Why does calling <code>bypassSecurityTrustHtml()</code> expose all users to stored Cross-Site Scripting (XSS)?
<br>
<strong>Part B:</strong> What are Angular's 4 distinct <strong>Security Contexts</strong> (HTML, Style, URL, ResourceURL)? What does Angular automatically sanitize by default when using <code>[innerHTML]=\"untrustedHtml\"</code>?
<br>
<strong>Part C:</strong> If an application genuinely needs to render rich user-submitted HTML (e.g. bold text, bullet points, links), how should an architect design a safe sanitization pipeline using <strong>DOMPurify</strong> before trusting the string?""",
        "snippet_title": "notice-board.component.ts",
        "snippet_code": """@Component({
  selector: 'app-notice-board',
  standalone: true,
  template: `<div [innerHTML]="trustedContent"></div>`
})
export class NoticeBoardComponent implements OnInit {
  @Input() rawNoticeHtml = '';
  trustedContent: SafeHtml = '';

  constructor(private sanitizer: DomSanitizer) {}

  ngOnInit() {
    // Critical Security Vulnerability: Blindly trusting raw input!
    this.trustedContent = this.sanitizer.bypassSecurityTrustHtml(this.rawNoticeHtml);
  }
}""",
        "rating_concept": "Angular security contexts, DomSanitizer XSS vulnerabilities, and DOMPurify pipelines",
        "solution": """<strong>Part A (The bypassSecurityTrust Vulnerability):</strong>
<br>• <code>bypassSecurityTrustHtml()</code> tells Angular: <em>\"Disable all internal XSS protection; I guarantee this string is safe.\"</em>
<br>• If the input contains malicious payloads (like <code>&lt;script&gt;</code>, <code>&lt;img onerror=...&gt;</code>, or <code>&lt;iframe&gt;</code>), the browser executes the attacker's JavaScript in the context of the authenticated user's session.
<br>• The attacker can steal JWTs, access session storage, or make unauthorized API calls on behalf of the victim.
<br><br>
<strong>Part B (Angular's 4 Security Contexts):</strong>
<br>1. <strong>HTML:</strong> Used in <code>[innerHTML]</code>. Strips unsafe elements (<code>&lt;script&gt;</code>, <code>&lt;object&gt;</code>) and dangerous attributes (<code>onerror</code>, <code>onclick</code>).
<br>2. <strong>Style:</strong> Used in <code>[style.xyz]</code>. Prevents CSS injection (e.g. <code>expression()</code> or background tracking URLs).
<br>3. <strong>URL:</strong> Used in <code>&lt;a [href]&gt;</code>. Blocks <code>javascript:</code> pseudoprotocols.
<br>4. <strong>ResourceURL:</strong> Used in <code>&lt;script [src]&gt;</code> or <code>&lt;iframe [src]&gt;</code>. Must be explicitly trusted because it executes executable code.
<br><br>
<strong>Part C (Safe Sanitization via DOMPurify):</strong>
<br>Never bypass security on raw strings. Sanitize the string first with a dedicated DOM sanitization library like <strong>DOMPurify</strong>, and only then wrap it in <code>bypassSecurityTrustHtml()</code>.""",
        "optimized_code": """import DOMPurify from 'dompurify';

@Component({
  selector: 'app-notice-board',
  standalone: true,
  template: `<div [innerHTML]="cleanHtml"></div>`
})
export class NoticeBoardComponent {
  private sanitizer = inject(DomSanitizer);

  cleanHtml = computed(() => {
    // 1. Sanitize with DOMPurify to strip malicious scripts/attributes
    const clean = DOMPurify.sanitize(this.rawHtmlInput());
    // 2. Safe to mark trusted after purification
    return this.sanitizer.bypassSecurityTrustHtml(clean);
  });
}""",
        "junior_eval": "Uses bypassSecurityTrustHtml() indiscriminately on user-generated content or thinks Angular automatically sanitizes strings passed to bypassSecurityTrustHtml().",
        "expert_eval": "Explains Angular security contexts, details DOM-based XSS vectors, and builds a two-stage sanitization pipeline using DOMPurify before trusting HTML."
    })

    # Q17: View Encapsulation & Style Scoping
    questions.append({
        "id": 17,
        "badge": "Styling & Component Encapsulation",
        "keywords": "view encapsulation emulated shadowdom none ng-deep host global pollution",
        "concept": "Angular ViewEncapsulation modes (<code>Emulated</code>, <code>ShadowDom</code>, <code>None</code>), CSS host attribute generation, avoiding global style pollution, and migrating away from <code>::ng-deep</code>.",
        "question": """A team builds a shared button component for a corporate design system. Look at the component code snippet.
<br><br>
<strong>Part A:</strong> A developer sets <code>encapsulation: ViewEncapsulation.None</code> to easily style an internal element. After deployment, all primary buttons across the entire multi-team enterprise portal suddenly turn hot pink! Why does <code>ViewEncapsulation.None</code> cause global stylesheet pollution?
<br>
<strong>Part B:</strong> How does <strong><code>ViewEncapsulation.Emulated</code></strong> (default) isolate styles using dynamically generated HTML host attributes like <code>_ngcontent-xyz</code>?
<br>
<strong>Part C:</strong> Why is <code>::ng-deep</code> deprecated, and how should an architect design themeable design system components using <strong>CSS Custom Properties (Variables)</strong> instead?""",
        "snippet_title": "custom-button.component.ts",
        "snippet_code": """@Component({
  selector: 'app-custom-button',
  standalone: true,
  encapsulation: ViewEncapsulation.None,
  styles: [`
    /* Catastrophic Style Leak: Overrides all .btn elements globally */
    .btn {
      background-color: #ff1493 !important;
      padding: 12px 24px;
    }
  `],
  template: `<button class="btn"><ng-content></ng-content></button>`
})
export class CustomButtonComponent {}""",
        "rating_concept": "ViewEncapsulation modes, Emulated attribute scoping, and CSS Custom Properties",
        "solution": """<strong>Part A (Global Stylesheet Pollution with None):</strong>
<br>• Under <code>ViewEncapsulation.None</code>, Angular injects component styles directly into the global HTML <code>&lt;head&gt;</code> without any scoping or attribute prefixes.
<br>• Rules matching general classes (like <code>.btn</code> or <code>p</code>) apply globally across the entire DOM tree, overriding styles in completely unrelated components.
<br><br>
<strong>Part B (How Emulated Scoping Works Internally):</strong>
<br>• Angular's compiler parses the component's CSS rules and appends unique generated attribute selectors:
<br><code>.btn[_ngcontent-ng-c12345] { background-color: ... }</code>
<br>• In the template HTML, Angular automatically adds matching attributes to the elements:
<br><code>&lt;button class=\"btn\" _ngcontent-ng-c12345&gt;...&lt;/button&gt;</code>
<br>• The browser's CSS engine naturally scopes the styles to only those specific elements.
<br><br>
<strong>Part C (Replacing ::ng-deep with CSS Custom Properties):</strong>
<br>• <code>::ng-deep</code> punches through view encapsulation boundaries, violating component isolation and coupling parent styling to child internal DOM structures.
<br>• <strong>Modern Solution:</strong> Expose CSS custom properties in the child component:
<br><code>.btn { background-color: var(--button-bg, #007bff); }</code>
<br>Parent components can override <code>--button-bg</code> cleanly without penetrating internal DOM hierarchies.""",
        "optimized_code": """@Component({
  selector: 'app-custom-button',
  standalone: true,
  encapsulation: ViewEncapsulation.Emulated, // Default: Safe Scoping
  styles: [`
    :host {
      display: inline-block;
    }
    .btn {
      background-color: var(--btn-color, #2563eb);
      padding: 10px 20px;
    }
  `],
  template: `<button class="btn"><ng-content></ng-content></button>`
})
export class CustomButtonComponent {}""",
        "junior_eval": "Uses ViewEncapsulation.None or litters stylesheets with ::ng-deep to override child component styling.",
        "expert_eval": "Explains Emulated host attribute post-processing (_ngcontent), details global stylesheet leaks, and architecturally exposes CSS custom properties for theming."
    })

    # Q18: Pure vs Impure Pipes Mechanics
    questions.append({
        "id": 18,
        "badge": "Pipes & Performance Ergonomics",
        "keywords": "pipes pure impure change detection memoization filtering sorting anti pattern",
        "concept": "Angular Custom Pipes, Pure vs Impure pipe change detection mechanics, memoization, and why filtering/sorting arrays in templates using pipes is an architectural anti-pattern.",
        "question": """A developer implements a custom search filter pipe to filter a list of 5,000 customers in a template. Look at the pipe code snippet.
<br><br>
<strong>Part A:</strong> The pipe is declared with <code>pure: false</code>. Whenever a user moves their mouse, types in a text box, or an HTTP polling request finishes, the browser UI freezes. Explain why <strong>Impure Pipes</strong> cause catastrophic performance degradation.
<br>
<strong>Part B:</strong> How does a <strong>Pure Pipe</strong> determine when to execute its <code>transform()</code> method? What happens if you pass a mutated array to a pure pipe?
<br>
<strong>Part C:</strong> Why does the official Angular documentation explicitly recommend <em>against</em> building filter and sort pipes? What is the architecturally sound pattern for search and filtering?""",
        "snippet_title": "filter-customers.pipe.ts",
        "snippet_code": """@Pipe({
  name: 'filterCustomers',
  pure: false, // Impure Pipe Anti-Pattern for large collections
  standalone: true
})
export class FilterCustomersPipe implements PipeTransform {
  transform(customers: Customer[], searchTerm: string): Customer[] {
    if (!customers || !searchTerm) return customers;
    // Heavy calculation executing dozens of times per second!
    return customers.filter(c => 
      c.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }
}""",
        "rating_concept": "Pure vs Impure Pipes, change detection frequency, and Signals/RxJS filtering alternatives",
        "solution": """<strong>Part A (The Impure Pipe Execution Disaster):</strong>
<br>• An <strong>Impure Pipe</strong> (<code>pure: false</code>) is executed on <strong>every single change detection cycle</strong> across the entire application, regardless of whether its input arguments changed!
<br>• In an application with background timers, mouse events, or network calls, change detection may run 20–60 times per second.
<br>• Filtering an array of 5,000 items 60 times a second creates millions of string allocations and garbage collection pressure, completely freezing the browser main thread.
<br><br>
<strong>Part B (Pure Pipe Change Detection):</strong>
<br>• A <strong>Pure Pipe</strong> executes only when its input parameters change by <strong>primitive value or object reference</strong> (<code>===</code>).
<br>• If you mutate an array in-place (<code>customers.push(newCustomer)</code>) without changing the array reference, a pure pipe <strong>will not re-execute</strong>, and the UI will fail to update.
<br><br>
<strong>Part C (The Architectural Alternative):</strong>
<br>• Pipes in templates should strictly be used for simple formatting (Currency, Date, Uppercase).
<br>• Filtering and sorting should be handled in the component class or state layer using <strong>Signals or RxJS</strong>:
<br><code>filteredCustomers = computed(() => this.customers().filter(...));</code>
<br>This guarantees execution occurs only when the search term or customer list actually changes.""",
        "optimized_code": """@Component({
  selector: 'app-customer-list',
  standalone: true,
  template: `
    @for (c of filteredCustomers(); track c.id) {
      <div>{{ c.name }}</div>
    }
  `
})
export class CustomerListComponent {
  customers = signal<Customer[]>([]);
  searchTerm = signal<string>('');

  // Clean, high-performance derivation using Signals
  filteredCustomers = computed(() => {
    const term = this.searchTerm().toLowerCase();
    return this.customers().filter(c => c.name.toLowerCase().includes(term));
  });
}""",
        "junior_eval": "Sets pure: false to make a broken filter pipe update, causing massive CPU throttling across the application.",
        "expert_eval": "Identifies that impure pipes execute on every change detection cycle, explains pure pipe reference checking, and moves collection filtering into computed Signals."
    })

    # Q19: Micro Frontends with Angular & Module Federation
    questions.append({
        "id": 19,
        "badge": "Enterprise Micro Frontends & Federation",
        "keywords": "micro frontends module federation webpack shared singletons angular core elements",
        "concept": "Angular Micro Frontends using Webpack/Vite Module Federation, sharing core libraries as singletons (<code>@angular/core</code>, <code>rxjs</code>), and framework-agnostic Angular Elements.",
        "question": """An enterprise migrates a large banking portal into a Micro Frontend architecture consisting of a Shell application and two remote micro-apps (Payment App and Accounts App). Look at the Webpack Module Federation snippet.
<br><br>
<strong>Part A:</strong> When the Shell app loads the remote Payment micro-app, the browser console throws: <code>NG0200: Circular dependency</code> and <code>Platform already exists</code>. Why does failing to declare <code>@angular/core</code> as a <strong>shared singleton</strong> cause Angular to crash at runtime?
<br>
<strong>Part B:</strong> What is the difference between <code>singleton: true</code> and <code>strictVersion: true</code> in Module Federation? What happens if the Shell uses Angular 17.1 and the remote app uses Angular 17.3?
<br>
<strong>Part C:</strong> How do <strong>Angular Elements</strong> (<code>createCustomElement</code>) allow publishing an Angular component as a standard Web Component usable by React or Vue hosts?""",
        "snippet_title": "webpack.config.js",
        "snippet_code": """const { shareAll, withModuleFederationPlugin } = require('@angular-architects/module-federation/webpack');

module.exports = withModuleFederationPlugin({
  name: 'payment-remote',
  exposes: {
    './PaymentModule': './src/app/payment/payment.routes.ts',
  },
  // Anti-Pattern: Missing shared configuration!
  shared: {}
});""",
        "rating_concept": "Module Federation, shared singletons (@angular/core), and Angular Elements Web Components",
        "solution": """<strong>Part A (The Multiple Angular Runtime Collision):</strong>
<br>• Angular relies on global singletons stored in its runtime: the <code>PlatformRef</code>, the Root Injector, and Zone.js.
<br>• If <code>@angular/core</code> is not shared as a singleton, the Shell bundles its own copy of Angular, and the remote app bundles a second copy of Angular.
<br>• When the remote loads, it attempts to initialize a second <code>PlatformRef</code> in the same browser window, triggering fatal runtime crashes (<code>Cannot create platform when another platform exists</code>).
<br><br>
<strong>Part B (singleton vs strictVersion in Module Federation):</strong>
<br>• <code>singleton: true</code>: Guarantees that only <strong>one instance</strong> of the library is loaded in memory and shared across all micro-frontends.
<br>• <code>strictVersion: true</code>: If host and remote have mismatched semver versions (e.g. 17.1 vs 17.3), Webpack refuses to share and fails with an error.
<br>• If <code>strictVersion: false</code> (recommended for minor version variance), Webpack picks the highest compatible version.
<br><br>
<strong>Part C (Angular Elements & Web Components):</strong>
<br>• <code>createCustomElement(MyComponent, { injector })</code> bridges the Angular component into a native W3C Custom Element.
<br>• <code>customElements.define('payment-widget', element)</code> registers it with the browser.
<br>• A React, Vue, or vanilla JS host can render <code>&lt;payment-widget [amount]=\"100\"&gt;&lt;/payment-widget&gt;</code> natively without knowing Angular exists.""",
        "optimized_code": """module.exports = withModuleFederationPlugin({
  name: 'payment-remote',
  exposes: {
    './PaymentRoutes': './src/app/payment/payment.routes.ts',
  },
  shared: {
    ...shareAll({ 
      singleton: true, 
      strictVersion: true, 
      requiredVersion: 'auto' 
    })
  }
});""",
        "junior_eval": "Treats micro-frontends like standard iframes or fails to configure shared singletons for @angular/core and rxjs.",
        "expert_eval": "Diagnoses duplicate platform initialization collisions, configures Module Federation shared singleton contracts, and bridges components via Angular Elements."
    })

    # Q20: Core Web Vitals & Performance Profiling
    questions.append({
        "id": 20,
        "badge": "Core Web Vitals & Optimization",
        "keywords": "core web vitals lcp cls inp ngoptimizedimage bundle budget devtools profiler",
        "concept": "Optimizing Core Web Vitals in Angular (Largest Contentful Paint - LCP, Cumulative Layout Shift - CLS, Interaction to Next Paint - INP), <code>NgOptimizedImage</code>, and bundle budgets.",
        "question": """An e-commerce portal fails Google's Core Web Vitals audit with an LCP of 6.2s, a CLS of 0.35, and an initial main bundle of 8 MB. Look at the template and configuration snippet.
<br><br>
<strong>Part A:</strong> How does switching raw <code>&lt;img src=\"...\"&gt;</code> tags to the modern <strong><code>NgOptimizedImage</code> directive</strong> (<code>&lt;img ngSrc=\"...\"&gt;</code>) eliminate Cumulative Layout Shift (CLS) and accelerate LCP?
<br>
<strong>Part B:</strong> What is <strong>INP (Interaction to Next Paint)</strong>, and how do long-running JavaScript execution tasks on the Angular main thread degrade INP scores?
<br>
<strong>Part C:</strong> How do you configure <strong>bundle budgets</strong> in <code>angular.json</code> to enforce that production initial bundles cannot exceed 500 KB, failing continuous integration builds if a developer introduces a heavy dependency?""",
        "snippet_title": "product-card.component.html",
        "snippet_code": """<!-- Unoptimized HTML hurting LCP and CLS -->
<div class="product-card">
  <img src="https://cdn.example.com/images/hero-laptop.jpg">
  <h3>Ultra Laptop Pro</h3>
</div>

<!-- angular.json Bundle Budget Anti-Pattern: Unlimited size! -->
"budgets": [
  {
    "type": "initial",
    "maximumWarning": "10mb",
    "maximumError": "20mb"
  }
]""",
        "rating_concept": "Core Web Vitals (LCP, CLS, INP), NgOptimizedImage, and angular.json bundle budgets",
        "solution": """<strong>Part A (NgOptimizedImage Benefits for LCP & CLS):</strong>
<br>• <strong>CLS Elimination:</strong> <code>NgOptimizedImage</code> requires explicit <code>width</code> and <code>height</code> attributes (or <code>fill</code>), forcing the browser to allocate exact layout space before the image loads, eliminating layout shift (CLS = 0).
<br>• <strong>LCP Optimization:</strong> Marking the hero image with the <code>priority</code> attribute automatically generates a <code>&lt;link rel=\"preload\"&gt;</code> header in the HTML, fetching the hero image at the highest network priority.
<br>• Automatically generates responsive <code>srcset</code> attributes to serve properly scaled WebP/AVIF images.
<br><br>
<strong>Part B (INP & Long Tasks):</strong>
<br>• <strong>INP (Interaction to Next Paint):</strong> Measures user interface responsiveness from the moment a user clicks, taps, or types until the next frame is visually presented.
<br>• Heavy synchronous computations in change detection, large loops, or un-debounced inputs block the browser's single JavaScript main thread.
<br>• If the main thread is blocked for > 200ms, user clicks lag, resulting in an unacceptable INP score.
<br><br>
<strong>Part C (Enforcing Bundle Budgets in angular.json):</strong>
<br>Set strict budgets in <code>angular.json</code> under the production configuration:
<br><code>\"maximumWarning\": \"300kb\", \"maximumError\": \"500kb\"</code>.
<br>If a developer imports a monolithic library (like <code>lodash</code> or <code>moment.js</code>), <code>ng build</code> throws a compile-time build error, blocking the pull request.""",
        "optimized_code": """<!-- Optimized Template with NgOptimizedImage -->
<img [ngSrc]="product.imageUrl" 
     width="600" 
     height="400" 
     priority 
     alt="Laptop">

<!-- Strict angular.json Production Budget -->
"budgets": [
  {
    "type": "initial",
    "maximumWarning": "400kb",
    "maximumError": "500kb"
  },
  {
    "type": "anyComponentStyle",
    "maximumWarning": "4kb",
    "maximumError": "8kb"
  }
]""",
        "junior_eval": "Increases angular.json budget thresholds to 15MB to silence build warnings or leaves image dimensions undefined in templates.",
        "expert_eval": "Implements NgOptimizedImage with priority preloading to optimize LCP and CLS, enforces strict <500KB bundle budgets in CI/CD, and audits long tasks to optimize INP."
    })

    return questions

def generate_angular_html():
    from create_angular_page import html_header, html_footer
    questions = get_angular_questions()

    cards_html = []

    for q in questions:
        q_id = q["id"]
        keywords = html.escape(q["keywords"])
        badge = html.escape(q["badge"])
        concept = q["concept"]
        question_text = q["question"]
        snippet_title = html.escape(q["snippet_title"])
        
        # Clean snippet code programmatically to ensure ZERO comments in candidate snippets
        clean_lines = []
        for line in q["snippet_code"].split("\n"):
            # strip single-line comments (// or /* or <!--)
            if "//" in line and "http://" not in line and "https://" not in line:
                idx = line.find("//")
                line = line[:idx].rstrip()
            if "/*" in line and "*/" in line:
                idx1 = line.find("/*")
                idx2 = line.find("*/")
                line = (line[:idx1] + line[idx2+2:]).rstrip()
            if line.strip().startswith("<!--") and line.strip().endswith("-->"):
                line = ""
            if line.strip():
                clean_lines.append(line)
        clean_snippet = "\n".join(clean_lines)
        snippet_code_escaped = html.escape(clean_snippet)
        
        rating_concept_escaped = html.escape(q["rating_concept"]).replace("'", "\\'")
        solution_text = q["solution"]
        optimized_code = html.escape(q["optimized_code"])
        junior_eval = html.escape(q["junior_eval"])
        expert_eval = html.escape(q["expert_eval"])

        card = f"""                <!-- QUESTION {q_id}: {badge} -->
                <div class="question-card" id="q-{q_id}" data-keywords="{keywords}">
                    <div class="card-header">
                        <span class="concept-badge">{badge}</span>
                        <span class="q-number">Question {q_id} of 20</span>
                    </div>
                    <div class="card-body">
                        <div class="section-block">
                            <div class="section-title">📌 1. Concept Covered</div>
                            <div class="concept-text">
                                {concept}
                            </div>
                        </div>

                        <div class="section-block">
                            <div class="section-title">❓ 2. Question</div>
                            <div class="question-title">
                                {question_text}
                            </div>
                        </div>

                        <div class="section-block">
                            <div class="section-title">💻 3. Code Challenge</div>
                            <button class="btn-view-code" onclick="openCodeSnippetModal('{q_id}', '{snippet_title}')">
                                💻 View Code Snippet (Popup)
                            </button>
                            <div id="snippet-{q_id}" style="display:none;">{snippet_code_escaped}</div>
                        </div>

                        <!-- 1-4 Answer Quality Rating -->
                        <div class="question-rating-panel">
                            <span class="rating-panel-label">🎯 Answer Quality:</span>
                            <div class="star-rating-group" id="star-group-{q_id}">
                                <button class="star-btn" data-rating="1" onclick="setQuestionRating('angular', {q_id}, 1, '{rating_concept_escaped}')">
                                    <span class="star-num">1</span>
                                    <span class="star-label">Cannot Explain</span>
                                </button>
                                <button class="star-btn" data-rating="2" onclick="setQuestionRating('angular', {q_id}, 2, '{rating_concept_escaped}')">
                                    <span class="star-num">2</span>
                                    <span class="star-label">Partial</span>
                                </button>
                                <button class="star-btn" data-rating="3" onclick="setQuestionRating('angular', {q_id}, 3, '{rating_concept_escaped}')">
                                    <span class="star-num">3</span>
                                    <span class="star-label">Good</span>
                                </button>
                                <button class="star-btn" data-rating="4" onclick="setQuestionRating('angular', {q_id}, 4, '{rating_concept_escaped}')">
                                    <span class="star-num">4</span>
                                    <span class="star-label">Expert</span>
                                </button>
                            </div>
                            <span class="q-score-display" id="q-score-{q_id}">Not Rated</span>
                        </div>

                        <button class="solution-toggle" onclick="toggleSolution(this)">
                            <span>👁️ Show Solution & Candidate Evaluation</span>
                            <span>▼</span>
                        </button>
                        <div class="solution-content">
                            <div class="solution-heading">Answer Key & Deep-Dive Explanation</div>
                            <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 8px;">
                                {solution_text}
                            </p>
                            <div class="code-wrapper">
                                <div class="code-header"><span>Architectural / Code Solution</span><span class="code-lang">TypeScript / HTML</span></div>
                                <pre><code>{optimized_code}</code></pre>
                            </div>
                            <div class="evaluation-grid">
                                <div class="eval-box eval-bad">
                                    <div class="eval-title">⚠️ Junior / Beginner Response</div>
                                    {junior_eval}
                                </div>
                                <div class="eval-box eval-good">
                                    <div class="eval-title">🌟 Advanced / Expert Response</div>
                                    {expert_eval}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
"""
        cards_html.append(card)

    all_cards_str = "\n".join(cards_html)
    full_html = html_header + all_cards_str + html_footer

    out_path = "/Users/barvepan/Pandharinath/Developer/Workspace/interview-questions/angular.html"
    with open(out_path, "w") as f:
        f.write(full_html)
    print(f"Generated {out_path} with {len(questions)} questions successfully!")

if __name__ == "__main__":
    generate_angular_html()

