import SideNav from "./SideNav.jsx"

export default function Invoices() {
  return (
    <div className="flex h-screen flex-col md:flex-row md:overflow-hidden">
      <div className="w-full flex-none md:w-64">
        <SideNav />
      </div>
      <div className="grow p-6 md:overflow-y-auto md:p-12">
        Invoices page
      </div>
    </div>    
  );
}
