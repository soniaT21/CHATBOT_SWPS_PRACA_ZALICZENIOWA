import Chat from "./chat";

export default function Page() {
  return (
    <main className="container py-4" style={{ maxWidth: 760 }}>
      <header className="text-center mb-4">
        <h1 className="h3 fw-bold mb-1">Asystent SWPS</h1>
        <p className="text-muted mb-0">
          Zapytaj o publikacje i badania Uniwersytetu SWPS.
        </p>
      </header>

      <Chat />

      <footer className="text-center text-muted small mt-4">
        Projekt zaliczeniowy · wersja podstawowa (wiedza z pliku general.md)
      </footer>
    </main>
  );
}
