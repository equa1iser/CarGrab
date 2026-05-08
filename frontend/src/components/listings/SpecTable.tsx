import { Vehicle } from "@/types";

interface Props {
  vehicle: Vehicle;
  mileage?: number | null;
  condition?: string | null;
  colorExterior?: string | null;
  colorInterior?: string | null;
}

export function SpecTable({ vehicle, mileage, condition, colorExterior, colorInterior }: Props) {
  const specs = [
    ["Year", vehicle.year],
    ["Make", vehicle.make],
    ["Model", vehicle.model],
    ["Trim", vehicle.trim],
    ["Body Style", vehicle.body_class],
    ["Drive Type", vehicle.drive_type],
    ["Fuel Type", vehicle.fuel_type],
    ["Engine", vehicle.engine],
    ["Doors", vehicle.doors],
    ["Seats", vehicle.seats],
    ["Mileage", mileage ? `${mileage.toLocaleString()} mi` : null],
    ["Condition", condition],
    ["Exterior Color", colorExterior],
    ["Interior Color", colorInterior],
  ].filter(([, v]) => v != null && v !== "");

  return (
    <div className="grid grid-cols-2 gap-x-6 gap-y-3">
      {specs.map(([label, value]) => (
        <div key={label} className="flex flex-col gap-0.5">
          <span className="text-xs font-medium uppercase tracking-wide text-cyan-400/70">{label}</span>
          <span className="text-sm text-white font-mono">{String(value)}</span>
        </div>
      ))}
    </div>
  );
}
