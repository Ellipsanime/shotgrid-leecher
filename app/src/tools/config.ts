import {parse} from "query-string";
import {keys, pipe, reduce, tryCatch} from "ramda";

type EnvUri = {[_: string]: string};

const CONFIG_KEY = "leecher.app.config";

export interface IConfig {
  activeUri: string;
  envUris: EnvUri;
}

export function swapKeysWithValues<A extends symbol, B extends symbol>(source: Record<A,B>): Record<B, A> {
  return  pipe(
    (x: Record<A,B>) => keys(x),
    reduce((acc: Record<B, A>, k: A) => ({...acc, [source[k]]: k} ), {} as Record<B, A>)
  )(source);
}

function parseEnvConfig(): IConfig {
  const queryString = process.env.REACT_APP_API_URIS || "";
  const parsed = parse(queryString);
  const parsedKeys = Object.keys(parsed);
  const envUris: EnvUri = parsedKeys.reduce((acc, x) => ({
    ...acc,
    ...{[x]: decodeURIComponent(`${parsed[x]}`)},
  }), {});
  return {
    activeUri: parsedKeys.length ? envUris[`${parsedKeys[0]}`] : "",
    envUris: envUris,
  };
}

export function activateUrl(url: string): void {
  const config = {...loadConfig(), activeUri: url};
  return localStorage.setItem(CONFIG_KEY, JSON.stringify(config))
}

export function loadConfig(): IConfig {
  const prevConfig = JSON.parse(localStorage.getItem(CONFIG_KEY) || "null");
  if (prevConfig) return prevConfig;
  return parseEnvConfig();
}

export function currentEnvName(): string {
  const conf = loadConfig();
  const swappedUris = swapKeysWithValues(conf.envUris) as Record<string, string>;
  return tryCatch(x => x[conf.activeUri], (_) => keys(conf.envUris)[0])(swappedUris) ;
}
