/**
 * Generate node codename from node location, type, and ID
 * Format: location_type_id (all lowercase, spaces replaced with -, separated by _)
 * If is_group is true, format becomes: location_type_group{id}
 */
export const generateNodeCodename = (
  location: string,
  type: string,
  id: string,
  is_group: boolean,
): string => {
  const formatString = (str: string) =>
    str.toLowerCase().replace(/\s+/g, "-").trim();

  const formattedId = is_group
    ? `group${formatString(id)}`
    : formatString(id);

  return `${formatString(location)}_${formatString(type)}_${formattedId}`;
};

/**
 * Parse node codename back to its components
 */
export const parseNodeCodename = (codename: string) => {
  const parts = codename.split("_");
  if (parts.length !== 3) {
    throw new Error("Invalid node codename format");
  }

  return {
    location: parts[0].replace(/-/g, " "),
    type: parts[1].replace(/-/g, " "),
    id: parts[2],
  };
};
