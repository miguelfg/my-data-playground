CREATE TABLE IF NOT EXISTS "offers_history" (
  "manufacturer_code" TEXT,
  "manufacturer_car_id" TEXT,

  "car_vin" TEXT,
  "car_id" TEXT,
  "car_license_plate" TEXT,
  "car_local_model_id" TEXT,
  "car_url_id" TEXT,

  "car_body_type" TEXT,
  "car_mileage" INTEGER,
  "car_price" REAL,
  "car_original_price" REAL,
  "car_catalogue_price" REAL,
  "car_martket_price" REAL,
  "car_price_excl_vat" REAL,
  "car_diff_prices" REAL,

  "car_transmission" TEXT,
  "car_fuel" TEXT,
  "car_gears" TEXT,
  "car_gearbox" TEXT,
  "car_power" TEXT,
  "car_power_kw" REAL,
  "car_power_cv" REAL,

  "car_model" TEXT,
  "car_model_name" TEXT,
  "car_model_year" INTEGER,
  "car_model_description" TEXT,
  "car_brand" TEXT,
  "car_type" TEXT,
  "car_package" TEXT,
  "car_description" TEXT,
  "car_engine" INTEGER,
  "car_exterior_color" TEXT,
  "car_interior_color" TEXT,
  "car_interior_style" TEXT,
  "car_acceleration" REAL,
  "car_max_speed" REAL,
  "car_pollution_badge" TEXT,
  "car_doors_num" TEXT,
  "car_seats" INTEGER,
  "car_height" INTEGER,
  "car_length" INTEGER,
  "car_width" INTEGER,

  "car_registration_year" INTEGER,
  "car_age_months" INTEGER,
  "car_registration_date" TEXT,

  -- "car_is_reserved" INTEGER,
  "car_approved" INTEGER,
  "car_vat_reclaimable" INTEGER,
  "car_rental_type" TEXT,
  "car_sale_status" TEXT,
  "car_financing_tae" TEXT,

  "car_url" TEXT,
  -- "car_source_url" TEXT,
  "car_views" INTEGER,
  "car_emissions_class" TEXT,
  "car_remaining_warranty" TEXT,
  "car_remaining_warranty_years" INTEGER,
  "car_date_offer" TEXT,
  "car_history_previous_usage" TEXT,

  "dealer_id" INTEGER,
  "dealer_name" TEXT,
  "dealer_phone" TEXT,
  "dealer_fax" TEXT,
  "dealer_country_code" TEXT,
  "dealer_location" TEXT,
  "dealer_region" INTEGER,
  "dealer_city" TEXT,
  "dealer_street" TEXT,
  "dealer_zip_code" INTEGER,
  "dealer_province" TEXT,
  "dealer_raw_id" INTEGER,
  "dealer_email" TEXT,
  "dealer_email_domain" TEXT,
  "dealer_website" TEXT,
  "dealer_geo_lat" REAL,
  "dealer_geo_lon" REAL,

  "source" TEXT,
  "source_url" TEXT
);

ALTER TABLE "offers_history" ADD COLUMN "last_seen" TIMESTAMP;
ALTER TABLE "offers_history" ADD COLUMN "last_seen_date" DATE;