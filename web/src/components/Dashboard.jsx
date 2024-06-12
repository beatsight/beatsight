import SideNav from "./SideNav.jsx"
// import { lusitana } from '../fonts';

export default function Dashboard() {
  return (
    <div className="flex h-screen flex-col md:flex-row md:overflow-hidden">
      <div className="w-full flex-none md:w-64">
        <SideNav />
      </div>
      <div className="grow p-6 md:overflow-y-auto md:p-12">
        <h1 className="mb-4 text-xl md:text-2xl">
          Dashboard
        </h1>

      </div>
    </div>    
  );
}
