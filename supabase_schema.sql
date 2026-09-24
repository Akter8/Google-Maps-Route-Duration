create table if not exists public.traffic_observations (
  id bigint generated always as identity primary key, timestamp_utc timestamptz not null,
  timestamp_local timestamptz not null, date_local date not null, day_of_week text not null,
  scheduled_slot timestamptz not null, route_id text not null check (route_id ~ '^R[1-6]$'),
  direction text not null check (direction in ('outbound', 'return')),
  duration_seconds double precision, static_duration_seconds double precision,
  traffic_delay_seconds double precision, distance_meters integer, api_success boolean not null,
  error_message text, created_at timestamptz not null default now(),
  constraint traffic_observations_route_slot_unique unique (route_id, scheduled_slot)
);
create table if not exists public.api_usage (
  month text primary key check (month ~ '^\\d{4}-\\d{2}$'), request_count integer not null default 0,
  last_updated timestamptz not null default now()
);
-- Atomic reservation prevents concurrent Actions jobs from exceeding the configured cap.
create or replace function public.reserve_google_request(p_month text, p_limit integer) returns boolean
language plpgsql security definer set search_path = public as $$
declare allowed boolean;
begin
  insert into api_usage(month, request_count) values (p_month, 0) on conflict (month) do nothing;
  update api_usage set request_count = request_count + 1, last_updated = now()
    where month = p_month and request_count < p_limit returning true into allowed;
  return coalesce(allowed, false);
end; $$;
grant all on public.traffic_observations, public.api_usage to service_role;
grant execute on function public.reserve_google_request(text, integer) to service_role;
