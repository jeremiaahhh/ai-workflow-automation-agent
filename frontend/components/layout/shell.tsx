import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";

export function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Topbar />
        <main className="flex-1 px-6 pb-12 pt-8 sm:px-8">
          <div className="mx-auto max-w-7xl space-y-8 animate-fade-in">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
